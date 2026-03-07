import os
from datetime import datetime
from .package_identifier import PackageIdentifier

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

                    self.valid_files.append({
                        'path': file_path,
                        'relative_path': relative_path,
                        'name': file,
                        'size': os.path.getsize(file_path),
                        'modified': datetime.fromtimestamp(os.path.getmtime(file_path)),
                        'package_type': package_type,  # 包类型
                        'package_details': details  # 包详情
                    })
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
