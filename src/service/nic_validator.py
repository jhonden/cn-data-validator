# -*- coding: utf-8 -*-
"""NIC 包深度校验模块

校验 NIC 包中的网元数据完整性，包括：
- 网元元数据解析
- 网元数据文件夹检查
- 关键文件缺失校验
- 采集时间范围校验
- 网元级别静态 MML 校验
"""

import os
import re
import tarfile
import tempfile
import sys
from typing import Dict, List, Optional, Set
from datetime import datetime
import xml.etree.ElementTree as ET

# Import static MML checker
from .static_mml.static_mml_checker import StaticMMLChecker
from .scenario_checker import ScenarioChecker


def get_resource_path(relative_path: str) -> str:
    """
    获取资源文件的绝对路径，支持开发环境和打包环境

    Args:
        relative_path: 相对于当前模块的相对路径

    Returns:
        资源文件的绝对路径
    """
    try:
        # PyInstaller 打包后的临时目录
        base_path = sys._MEIPASS
        # 在打包后，资源文件直接放在 _MEIPASS 的 src/config 子目录中
        return os.path.join(base_path, 'src', 'config', os.path.basename(relative_path))
    except AttributeError:
        # 开发环境，使用当前文件所在目录
        return os.path.join(os.path.dirname(__file__), '..', '..', 'config', relative_path)


class NEInstance:
    """网元实例信息"""

    def __init__(self, name: str, ne_type: str, instance_id: str,
                 group_id: str, ip: str):
        self.name = name
        self.ne_type = ne_type
        self.instance_id = instance_id
        self.group_id = group_id
        self.ip = ip

    @property
    def folder_name(self) -> str:
        """生成网元数据文件夹名称"""
        # 将 IP 中的点替换为下划线
        ip_formatted = self.ip.replace('.', '_')
        return f"{self.ne_type}_{self.instance_id}_IP_{ip_formatted}_{self.group_id}_{self.name}"

    def __repr__(self):
        return f"NEInstance(name={self.name}, type={self.ne_type}, id={self.instance_id})"


class NICValidator:
    """NIC 包校验器"""

    # 支持的网元类型全集
    SUPPORTED_NE_TYPES = {
        'UNC', 'UDG', 'vCG', 'vUGW', 'vUSN', 'ATS', 'CSCF',
        'CloudSE2980', 'SE2900', 'CCF', 'SPSV3', 'USC',
        'HSS9860', 'UDM', 'UPCC', 'UPCF', 'ENS', 'USCDB',
        'CSP', 'CGPOMU'
    }

    # 网元类型到关键文件的映射
    # key: 网元类型, value: 关键文件列表
    NE_REQUIRED_FILES = {
        'CSCF': [
            ('static_mml', '静态MML配置'),
            ('dynamic_mml', '动态MML配置'),
            ('statistics', '话统文件')
        ],
        'ATS': [
            ('static_mml', '静态MML配置'),
            ('dynamic_mml', '动态MML配置'),
            ('statistics', '话统文件')
        ],
        # 默认规则（其他网元类型）
        'default': [
            ('static_mml', '静态MML配置'),
            ('dynamic_mml', '动态MML配置'),
            ('statistics', '话统文件')
        ]
    }

    def __init__(self, nic_path: str, report_file: Optional[str] = None):
        """
        初始化 NIC 包校验器

        Args:
            nic_path: NIC 包文件路径（.tar.gz）
            report_file: NIC 包对应的报告文件路径（可选）
        """
        self.nic_path = nic_path
        self.report_file = report_file
        self.ne_instances: List[NEInstance] = []
        self.neinfo_path = None
        self.temp_dir = None
        # Initialize checkers
        config_path = get_resource_path('static_mml_config.yaml')
        self.static_mml_checker = StaticMMLChecker(config_path)
        scenario_config_path = get_resource_path('scenario_config.yaml')
        self.scenario_checker = ScenarioChecker(scenario_config_path)

    def validate(self) -> Dict:
        """
        执行完整的 NIC 包校验

        Returns:
            校验结果字典，包含：
            - valid: 是否通过校验
            - neinfo_exists: neinfo.txt 是否存在
            - unsupported_types: 不支持的网元类型列表
            - missing_folders: 缺失的网元数据文件夹
            - missing_files: 缺失的关键文件 {folder_name: [missing_file_types]}
            - collect_range_too_short: 采集时间范围是否过短
            - collect_range_hours: 采集时间范围（小时）
            - anonymous_mode_invalid: 是否为匿名化采集
            - anonymous_mode: 匿名化模式值（true/false）
            - warnings: 警告信息列表
            - errors: 错误信息列表
        """
        result = {
            'valid': True,
            'neinfo_exists': False,
            'unsupported_types': [],
            'missing_folders': [],
            'missing_files': {},
            'collect_range_too_short': False,
            'collect_range_hours': None,
            'anonymous_mode_invalid': False,
            'anonymous_mode': None,
            'warnings': [],
            'errors': [],
            'static_mml_validation': None  # Add static MML validation result
        }

        try:
            # 1. 解压 NIC 包
            self.temp_dir = tempfile.mkdtemp(prefix='nic_validation_')
            self._extract_nic_package()

            # 2. 查找并解析 neinfo.txt
            self.neinfo_path = self._find_neinfo_file()
            if not self.neinfo_path:
                result['valid'] = False
                result['errors'].append("Invalid NIC package format: Missing required file neinfo.txt")
                result['missing_neinfo'] = True
                return result

            result['neinfo_exists'] = True
            self._parse_neinfo_file(result)

            # 3. 检查采集时间范围和匿名化模式
            self._check_collect_range(result)
            self._check_anonymous_mode(result)

            # 4. 检查网元数据文件夹是否存在
            self._check_ne_folders(result)

            # 5. 检查关键文件 (已禁用 - 与网元级 static_mml 校验重复)
            # self._check_required_files(result)

            # 6. 检查网元级别静态 MML
            self._check_static_mml(result)

            # 7. 判断整体校验结果
            # 只有当所有网元类型都不支持时，才标记为无效
            # 如果有任何一个网元类型支持，即使有其他不支持的，也算部分有效
            all_unsupported = len(self.ne_instances) > 0 and len(result['unsupported_types']) == len(self.ne_instances)

            # Package-level issues only (NE-level issues like missing_files are excluded)
            # Use .get() to avoid KeyError when keys don't exist
            if result.get('collect_range_too_short') or result.get('missing_folders') or result.get('missing_neinfo') or all_unsupported:
                result['valid'] = False
                # 标记是否完全不支持的包
                result['all_unsupported'] = all_unsupported

        except Exception as e:
            result['valid'] = False
            result['errors'].append(f"Validation error: {str(e)}")

        finally:
            # 清理临时目录
            if self.temp_dir and os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir, ignore_errors=True)

        return result

    def _extract_nic_package(self):
        """解压 NIC 包到临时目录"""
        with tarfile.open(self.nic_path, 'r:gz') as tar:
            tar.extractall(self.temp_dir)

    def _find_neinfo_file(self) -> Optional[str]:
        """在 NIC 包中查找 neinfo.txt 文件"""
        for root, dirs, files in os.walk(self.temp_dir):
            if 'neinfo.txt' in files:
                return os.path.join(root, 'neinfo.txt')
        return None

    def _parse_neinfo_file(self, result: Dict):
        """解析 neinfo.txt 文件"""
        try:
            with open(self.neinfo_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    # 解析行（可能有多个空格）
                    parts = re.split(r'\s+', line)
                    if len(parts) < 4:
                        result['warnings'].append(f"Line {line_num}: Invalid format, expected at least 4 fields")
                        continue

                    name = parts[0]
                    type_instance = parts[1]
                    group_id = parts[2]
                    ip = parts[3]

                    # 解析 网元类型_网元实例ID
                    if '_' not in type_instance:
                        result['warnings'].append(f"Line {line_num}: Invalid type_instance format: {type_instance}")
                        continue

                    ne_type, instance_id = type_instance.split('_', 1)

                    # 检查网元类型是否支持
                    if ne_type not in self.SUPPORTED_NE_TYPES:
                        result['unsupported_types'].append({
                            'name': name,
                            'ne_type': ne_type,
                            'line': line_num
                        })

                    # 创建网元实例对象
                    ne_instance = NEInstance(name, ne_type, instance_id, group_id, ip)
                    self.ne_instances.append(ne_instance)

        except UnicodeDecodeError:
            # 尝试其他编码
            try:
                with open(self.neinfo_path, 'r', encoding='gbk') as f:
                    for line in f:
                        # 重复解析逻辑...
                        pass
            except Exception as e:
                result['errors'].append(f"Failed to read neinfo.txt: {str(e)}")

    def _check_ne_folders(self, result: Dict):
        """检查网元数据文件夹是否存在"""
        # 获取 neinfo.txt 所在目录（网元文件夹应该在这个目录下）
        neinfo_dir = os.path.dirname(self.neinfo_path)

        # 获取该目录下的所有文件夹
        existing_folders = set()
        for item in os.listdir(neinfo_dir):
            item_path = os.path.join(neinfo_dir, item)
            if os.path.isdir(item_path):
                existing_folders.add(item)

        # 检查每个网元的数据文件夹是否存在
        for ne_instance in self.ne_instances:
            expected_folder = ne_instance.folder_name
            if expected_folder not in existing_folders:
                result['missing_folders'].append({
                    'name': ne_instance.name,
                    'ne_type': ne_instance.ne_type,
                    'expected_folder': expected_folder
                })

    def _check_required_files(self, result: Dict):
        """检查网元数据文件夹中的关键文件"""
        neinfo_dir = os.path.dirname(self.neinfo_path)

        for ne_instance in self.ne_instances:
            folder_path = os.path.join(neinfo_dir, ne_instance.folder_name)

            # 跳过不存在的文件夹
            if not os.path.exists(folder_path):
                continue

            # 获取该网元类型需要校验的文件
            required_files = self.NE_REQUIRED_FILES.get(
                ne_instance.ne_type,
                self.NE_REQUIRED_FILES['default']
            )

            missing_files = []
            for file_type, file_desc in required_files:
                # 检查文件是否存在（可以是多种扩展名）
                files = os.listdir(folder_path)
                found = any(
                    file_type.lower() in f.lower()
                    for f in files
                )

                if not found:
                    missing_files.append({
                        'type': file_type,
                        'description': file_desc
                    })

            if missing_files:
                result['missing_files'][ne_instance.folder_name] = {
                    'ne_name': ne_instance.name,
                    'ne_type': ne_instance.ne_type,
                    'files': missing_files
                }

    def _check_static_mml(self, result: Dict):
        """Check NE-level static MML configuration and collection scenarios"""
        try:
            # Get NE folder path (directory containing neinfo.txt)
            ne_folder_path = os.path.dirname(self.neinfo_path)

            # Call static MML checker to validate all NEs
            static_mml_result = self.static_mml_checker.check_package(
                ne_folder_path,
                self.ne_instances
            )
            result['static_mml_validation'] = static_mml_result

            # Call scenario checker to validate collection scenarios
            scenario_result = self.scenario_checker.check_package(
                ne_folder_path,
                self.ne_instances
            )
            result['scenario_validation'] = scenario_result

        except Exception as e:
            result['warnings'].append(f"Error checking NE validations: {str(e)}")

    def _check_collect_range(self, result: Dict):
        """检查采集时间范围是否大于 24 小时"""
        try:
            # 查找 report.tar.gz 文件
            report_file_path = self._find_report_file()
            if not report_file_path:
                # report 文件不存在，跳过此项校验
                result['warnings'].append("Report file not found, skipping collection time range check")
                return

            # 解压 report.tar.gz
            self._extract_report_package(report_file_path)

            # 查找并解析 TaskExtValue.xml（同时解析采集时间范围和匿名化模式）
            collect_range = self._parse_collect_range(result)
            if not collect_range:
                result['warnings'].append("Failed to parse collection time range from TaskExtValue.xml")
                return

            # 计算时间差（小时）
            start_time, end_time = collect_range
            time_diff = end_time - start_time
            hours = time_diff.total_seconds() / 3600

            result['collect_range_hours'] = round(hours, 2)

            # 检查是否小于 24 小时
            if hours < 24:
                result['valid'] = False
                result['collect_range_too_short'] = True
                result['errors'].append(
                    "NIC package collection time range is too short, cannot support network assessment requirements. "
                    f"System requires at least 24h, please re-collect. (Actual: {hours:.2f}h)"
                )

        except Exception as e:
            result['warnings'].append(f"Error checking collection time range: {str(e)}")

    def _find_report_file(self) -> Optional[str]:
        """在临时目录中查找 report.tar.gz 文件"""
        for item in os.listdir(self.temp_dir):
            if item.endswith('_report.tar.gz'):
                return os.path.join(self.temp_dir, item)
        return None

    def _extract_report_package(self, report_file_path: str):
        """解压 report.tar.gz 到临时目录"""
        with tarfile.open(report_file_path, 'r:gz') as tar:
            tar.extractall(self.temp_dir)

    def _parse_collect_range(self, result: Dict) -> Optional[tuple]:
        """
        解析 TaskExtValue.xml 中的 CollectRange 标签和 AnonymousAuthMode 标签

        Returns:
            (start_time, end_time) 或 None
        """
        # 查找 taskparam/TaskExtValue.xml
        taskparam_path = os.path.join(self.temp_dir, 'taskparam')
        xml_path = os.path.join(taskparam_path, 'TaskExtValue.xml')

        if not os.path.exists(xml_path):
            return None

        try:
            # 解析 XML
            tree = ET.parse(xml_path)
            root = tree.getroot()

            # 查找 CollectRange 标签
            collect_range = root.find('.//CollectRange')
            if collect_range is None or collect_range.text is None:
                return None

            # 查找 AnonymousAuthMode 标签
            anonymous_mode = root.find('.//AnonymousAuthMode')
            if anonymous_mode is not None and anonymous_mode.text is not None:
                anonymous_mode_value = anonymous_mode.text.strip().lower()
                result['anonymous_mode'] = anonymous_mode_value == 'true'

            # 解析格式：开始时间|结束时间
            time_range = collect_range.text.strip()
            if '|' not in time_range:
                return None

            start_str, end_str = time_range.split('|', 1)

            # 解析时间格式：2025-03-20 21:15:18
            start_time = datetime.strptime(start_str.strip(), '%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(end_str.strip(), '%Y-%m-%d %H:%M:%S')

            return (start_time, end_time)

        except Exception as e:
            # XML 解析失败
            return None

    def _check_anonymous_mode(self, result: Dict):
        """检查是否为匿名化采集"""
        try:
            # 如果 anonymous_mode 未解析出来，说明 report 文件不存在或 XML 解析失败
            # 这种情况下跳过此校验
            if result.get('anonymous_mode') is None:
                return

            # 检查是否为匿名化模式（true）
            if result['anonymous_mode']:
                result['valid'] = False
                result['anonymous_mode_invalid'] = True
                result['errors'].append(
                    "The NIC package was collected in anonymous mode, cannot meet network assessment "
                    "requirements. Please re-collect in non-anonymous mode."
                )

        except Exception as e:
            result['warnings'].append(f"Error checking anonymous mode: {str(e)}")

    def get_summary(self) -> str:
        """获取校验结果摘要"""
        if not self.ne_instances:
            return "No NE instances found in neinfo.txt"

        total = len(self.ne_instances)
        unsupported = len([ne for ne in self.ne_instances
                           if ne.ne_type not in self.SUPPORTED_NE_TYPES])

        return f"Total: {total} NE instances, Unsupported: {unsupported}"
