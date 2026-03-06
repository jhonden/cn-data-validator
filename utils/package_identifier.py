"""
数据包类型识别器
用于识别不同类型的数据包（NIC、LCM、NFVI 等）
"""

import os
import tarfile
import tempfile
import shutil
import re
from datetime import datetime


class PackageIdentifier:
    """数据包类型识别器"""

    # 支持的包类型
    PACKAGE_TYPE_UNKNOWN = "未知"
    PACKAGE_TYPE_NIC = "NIC包"
    PACKAGE_TYPE_LCM = "LCM数据包"
    PACKAGE_TYPE_NFVI = "NFVI数据包"

    def __init__(self):
        pass

    def identify(self, file_path, file_name):
        """
        识别数据包类型

        Args:
            file_path: 文件的完整路径
            file_name: 文件名

        Returns:
            tuple: (package_type, details)
                package_type: 包类型（如 "NIC包"）
                details: 识别详情（字典，包含识别到的特征）
        """
        # 检查文件扩展名
        if file_name.endswith('.tar.gz'):
            return self._identify_tar_gz(file_path)
        elif file_name.endswith('.zip'):
            return self._identify_zip(file_path)
        elif file_name.endswith('.tar'):
            return self._identify_tar(file_path)
        elif file_name.endswith('.xlsx'):
            return (self.PACKAGE_TYPE_UNKNOWN, {"note": "Excel 文件，非数据包"})

        return (self.PACKAGE_TYPE_UNKNOWN, {"note": "不支持的文件格式"})

    def _identify_tar_gz(self, file_path):
        """识别 .tar.gz 文件"""
        try:
            # 尝试识别 NIC 包
            result = self._identify_nic_package(file_path)
            if result:
                return result

            # 未来可以添加其他类型的识别
            # result = self._identify_lcm_package(file_path)
            # if result:
            #     return result

            return (self.PACKAGE_TYPE_UNKNOWN, {"note": "无法识别的数据包类型"})

        except Exception as e:
            return (self.PACKAGE_TYPE_UNKNOWN, {"error": f"识别失败: {str(e)}"})

    def _identify_nic_package(self, file_path):
        """
        识别 NIC 包

        NIC 包特征：
        1. 是 .tar.gz 文件
        2. 解压后第一层级包含：
           - 时间格式命名的文件夹：YYYYMMDDHHMMSS
           - 对应的报告文件：{时间}_report.tar.gz
        3. 只有一个时间文件夹和一个报告文件

        Returns:
            tuple or None: (package_type, details) 如果是 NIC 包则返回，否则返回 None
        """
        try:
            # 创建临时目录解压
            with tempfile.TemporaryDirectory() as temp_dir:
                # 解压文件
                with tarfile.open(file_path, 'r:gz') as tar:
                    tar.extractall(temp_dir)

                # 获取第一层级的所有文件和文件夹
                first_level_items = os.listdir(temp_dir)

                # 如果不是正好两个项目，不是 NIC 包
                if len(first_level_items) != 2:
                    return None

                # 分类：文件夹和文件
                folders = []
                files = []

                for item in first_level_items:
                    item_path = os.path.join(temp_dir, item)
                    if os.path.isdir(item_path):
                        folders.append(item)
                    else:
                        files.append(item)

                # 必须有一个文件夹和一个文件
                if len(folders) != 1 or len(files) != 1:
                    return None

                # 检查文件夹名是否为时间格式：YYYYMMDDHHMMSS
                folder_name = folders[0]
                time_pattern = r'^\d{14}$'  # 14位数字

                if not re.match(time_pattern, folder_name):
                    return None

                # 验证时间是否有效
                try:
                    datetime.strptime(folder_name, '%Y%m%d%H%M%S')
                except ValueError:
                    return None

                # 检查文件名是否为 {文件夹名}_report.tar.gz
                expected_report_name = f"{folder_name}_report.tar.gz"
                file_name = files[0]

                if file_name != expected_report_name:
                    return None

                # 所有条件都满足，是 NIC 包
                return (
                    self.PACKAGE_TYPE_NIC,
                    {
                        "time": folder_name,
                        "report_file": file_name,
                        "structure": "时间文件夹 + 报告文件"
                    }
                )

        except Exception as e:
            # 解压或识别过程中出错，不是 NIC 包
            return None

    def _identify_zip(self, file_path):
        """识别 .zip 文件（待实现）"""
        return (self.PACKAGE_TYPE_UNKNOWN, {"note": "ZIP 文件识别待实现"})

    def _identify_tar(self, file_path):
        """识别 .tar 文件（待实现）"""
        return (self.PACKAGE_TYPE_UNKNOWN, {"note": "TAR 文件识别待实现"})

    def _identify_lcm_package(self, file_path):
        """识别 LCM 数据包（待实现）"""
        return None

    def _identify_nfvi_package(self, file_path):
        """识别 NFVI 数据包（待实现）"""
        return None
