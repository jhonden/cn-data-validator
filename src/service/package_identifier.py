# -*- coding: utf-8 -*-
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
    """数据包类型识别器 (Package Type Identifier)"""

    # 支持的包类型 (Supported Package Types)
    PACKAGE_TYPE_UNKNOWN = "Unknown"
    PACKAGE_TYPE_NIC = "NIC Package"
    PACKAGE_TYPE_LCM = "LCM Package"
    PACKAGE_TYPE_NFVI = "NFVI Package"

    def __init__(self):
        pass

    def identify(self, file_path, file_name):
        """
        识别数据包类型 (Identify Package Type)

        Args:
            file_path: 文件的完整路径 (Full file path)
            file_name: 文件名 (File name)

        Returns:
            tuple: (package_type, details)
                package_type: 包类型（如 "NIC Package"）(Package type)
                details: 识别详情（字典，包含识别到的特征）(Identification details)
        """
        # 检查文件扩展名 (Check file extension)
        if file_name.endswith('.tar.gz'):
            return self._identify_tar_gz(file_path)
        elif file_name.endswith('.zip'):
            return self._identify_zip(file_path)
        elif file_name.endswith('.tar'):
            return self._identify_tar(file_path)
        elif file_name.endswith('.xlsx'):
            return (self.PACKAGE_TYPE_UNKNOWN, {"note": "Excel 文件，非数据包 (Excel file, not a data package)"})
        return (self.PACKAGE_TYPE_UNKNOWN, {"note": "不支持的文件格式 (Unsupported file format)"})

    def _identify_tar_gz(self, file_path):
        """识别 .tar.gz 文件 (Identify .tar.gz files)"""
        try:
            # 尝试识别 NIC 包 (Try to identify NIC Package)
            result = self._identify_nic_package(file_path)
            if result:
                return result

            # 未来可以添加其他类型的识别 (Future can add other types)
            # result = self._identify_lcm_package(file_path)
            # if result:
            #     return result

            return (self.PACKAGE_TYPE_UNKNOWN, {"note": "无法识别的数据包类型 (Unable to identify package type)"})

        except Exception as e:
            return (self.PACKAGE_TYPE_UNKNOWN, {"error": f"识别失败: {str(e)} (Identification failed: {str(e)})"})

    def _identify_nic_package(self, file_path):
        """
        识别 NIC 包 (Identify NIC Package)

        NIC 包特征 (NIC Package Features):
        1. 是 .tar.gz 文件 (.tar.gz file)
        2. 解压后第一层级包含 (First level contains after extraction):
           - 时间格式命名的文件夹：YYYYMMDDHHMMSS (Time format folder)
           - 对应的报告文件：{时间}_report.tar.gz ({time}_report.tar.gz)
        3. 只有一个时间文件夹和一个报告文件 (Only one time folder and one report file)

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

                # 分类：文件夹和文件 (Classify: folders and files)
                folders = []
                files = []

                for item in first_level_items:
                    item_path = os.path.join(temp_dir, item)
                    if os.path.isdir(item_path):
                        folders.append(item)
                    else:
                        files.append(item)

                # 必须有一个文件夹和一个文件 (Must have one folder and one file)
                if len(folders) != 1 or len(files) != 1:
                    return None

                # 检查文件夹名是否为时间格式：YYYYMMDDHHMMSS (Check if folder name is time format: YYYYMMDDHHMMSS)
                folder_name = folders[0]
                time_pattern = r'^\d{14}$'  # 14位数字 (14 digits)

                if not re.match(time_pattern, folder_name):
                    return None

                # 验证时间是否有效 (Validate if time is valid)
                try:
                    datetime.strptime(folder_name, '%Y%m%d%H%M%S')
                except ValueError:
                    return None

                # 检查文件名是否为 {文件夹名}_report.tar.gz (Check if filename is {folder_name}_report.tar.gz)
                expected_report_name = f"{folder_name}_report.tar.gz"
                file_name = files[0]

                if file_name != expected_report_name:
                    return None

                # 所有条件都满足，是 NIC 包 (All conditions met, is NIC Package)
                return (
                    self.PACKAGE_TYPE_NIC,
                    {
                        "time": folder_name,
                        "report_file": file_name,
                        "structure": "时间文件夹 + 报告文件 (Time folder + Report file)"
                    }
                )

        except Exception as e:
            # 解压或识别过程中出错，不是 NIC 包 (Error during extraction or identification, not NIC Package)
            return None

    def _identify_zip(self, file_path):
        """识别 .zip 文件（待实现）(Identify .zip files - To be implemented)"""
        return (self.PACKAGE_TYPE_UNKNOWN, {"note": "ZIP 文件识别待实现 (ZIP file identification - To be implemented)"})

    def _identify_tar(self, file_path):
        """识别 .tar 文件（待实现）(Identify .tar files - To be implemented)"""
        return (self.PACKAGE_TYPE_UNKNOWN, {"note": "TAR 文件识别待实现 (TAR file identification - To be implemented)"})

    def _identify_lcm_package(self, file_path):
        """识别 LCM 数据包（待实现）(Identify LCM Package - To be implemented)"""
        return None

    def _identify_nfvi_package(self, file_path):
        """识别 NFVI 数据包（待实现）(Identify NFVI Package - To be implemented)"""
        return None
