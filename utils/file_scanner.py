# -*- coding: utf-8 -*-
import os
from datetime import datetime
from .package_identifier import PackageIdentifier
from .nic_validator import NICValidator

class FileScanner:
    """文件扫描器"""

    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.supported_extensions = ['.zip', '.tar.gz', '.tar', '.xlsx']
        self.illegal_files = []
        self.valid_files = []
        self.identifier = PackageIdentifier()  # 包识别器

    def scan_directory(self, progress_callback=None):
        """递归扫描目录

        Args:
            progress_callback: 进度回调函数，接收 0-100 的进度值
        """
        self.illegal_files = []
        self.valid_files = []

        # 先统计文件总数
        total_files = 0
        for root, dirs, files in os.walk(self.root_dir):
            total_files += len(files)

        processed = 0
        for root, dirs, files in os.walk(self.root_dir):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, self.root_dir)

                # 检查文件格式
                if self._is_valid_file(file):
                    # 识别包类型
                    package_type, details = self.identifier.identify(file_path, file)

                    file_info = {
                        'path': file_path,
                        'relative_path': relative_path,
                        'name': file,
                        'size': os.path.getsize(file_path),
                        'modified': datetime.fromtimestamp(os.path.getmtime(file_path)),
                        'package_type': package_type,  # 包类型
                        'package_details': details  # 包详情
                    }

                    # 如果是 NIC 包，执行深度校验
                    if package_type == 'NIC Package':
                        # 获取 report 文件名
                        report_file_name = details.get('report_file')
                        nic_validation = self._validate_nic_package(file_path, report_file_name)
                        file_info['nic_validation'] = nic_validation

                    self.valid_files.append(file_info)
                else:
                    self.illegal_files.append({
                        'path': file_path,
                        'relative_path': relative_path,
                        'name': file,
                        'size': os.path.getsize(file_path),
                        'modified': datetime.fromtimestamp(os.path.getmtime(file_path)),
                        'package_type': None,
                        'package_details': {'note': '文件格式非法'}
                    })

                # 报告进度
                processed += 1
                if progress_callback and total_files > 0:
                    progress = int((processed / total_files) * 100)
                    progress_callback(progress)

    def _is_valid_file(self, filename):
        """检查文件格式是否合法"""
        # 获取文件扩展名（正确处理带多个点的文件名）
        name_parts = filename.split('.')
        if len(name_parts) < 2:
            return False

        ext = '.' + '.'.join(name_parts[-2:]) if name_parts[-1] in ['gz'] else '.' + name_parts[-1]

        # 特殊处理 tar.gz
        if filename.endswith('.tar.gz'):
            ext = '.tar.gz'

        return ext.lower() in self.supported_extensions

    def get_statistics(self):
        """获取扫描统计"""
        return {
            'total_files': len(self.valid_files) + len(self.illegal_files),
            'valid_files': len(self.valid_files),
            'illegal_files': len(self.illegal_files)
        }

    def _validate_nic_package(self, nic_path: str, report_file_name: str = None):
        """校验 NIC 包中的网元数据

        Args:
            nic_path: NIC 包文件路径
            report_file_name: NIC 包对应的报告文件名（可选）

        Returns:
            NIC 校验结果字典
        """
        try:
            # 如果提供了 report_file_name，则尝试找到完整的 report 文件路径
            report_file_path = None
            if report_file_name:
                # report 文件应该在 NIC 包同级目录
                nic_dir = os.path.dirname(nic_path)
                report_file_path = os.path.join(nic_dir, report_file_name)

                # 如果不存在，可能在 NIC 包内部（已经解压在临时目录）
                if not os.path.exists(report_file_path):
                    report_file_path = None

            validator = NICValidator(nic_path, report_file_path)
            return validator.validate()
        except Exception as e:
            return {
                'valid': False,
                'error': f"NIC validation failed: {str(e)}",
                'neinfo_exists': False,
                'unsupported_types': [],
                'missing_folders': [],
                'missing_files': {},
                'warnings': [],
                'errors': [str(e)]
            }
