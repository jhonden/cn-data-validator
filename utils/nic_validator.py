"""NIC 包深度校验模块

校验 NIC 包中的网元数据完整性，包括：
- 网元元数据解析
- 网元数据文件夹检查
- 关键文件缺失校验
"""

import os
import re
import tarfile
import tempfile
from typing import Dict, List, Optional, Set


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

    def __init__(self, nic_path: str):
        """
        初始化 NIC 包校验器

        Args:
            nic_path: NIC 包文件路径（.tar.gz）
        """
        self.nic_path = nic_path
        self.ne_instances: List[NEInstance] = []
        self.neinfo_path = None
        self.temp_dir = None

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
            - warnings: 警告信息列表
            - errors: 错误信息列表
        """
        result = {
            'valid': True,
            'neinfo_exists': False,
            'unsupported_types': [],
            'missing_folders': [],
            'missing_files': {},
            'warnings': [],
            'errors': []
        }

        try:
            # 1. 解压 NIC 包
            self.temp_dir = tempfile.mkdtemp(prefix='nic_validation_')
            self._extract_nic_package()

            # 2. 查找并解析 neinfo.txt
            self.neinfo_path = self._find_neinfo_file()
            if not self.neinfo_path:
                result['valid'] = False
                result['errors'].append("neinfo.txt not found in NIC package")
                return result

            result['neinfo_exists'] = True
            self._parse_neinfo_file(result)

            # 3. 检查网元数据文件夹是否存在
            self._check_ne_folders(result)

            # 4. 检查关键文件
            self._check_required_files(result)

            # 5. 判断整体校验结果
            # 只有当所有网元类型都不支持时，才标记为无效
            # 如果有任何一个网元类型支持，即使有其他不支持的，也算部分有效
            all_unsupported = len(self.ne_instances) > 0 and len(result['unsupported_types']) == len(self.ne_instances)

            if result['missing_folders'] or result['missing_files'] or all_unsupported:
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

    def get_summary(self) -> str:
        """获取校验结果摘要"""
        if not self.ne_instances:
            return "No NE instances found in neinfo.txt"

        total = len(self.ne_instances)
        unsupported = len([ne for ne in self.ne_instances
                           if ne.ne_type not in self.SUPPORTED_NE_TYPES])

        return f"Total: {total} NE instances, Unsupported: {unsupported}"
