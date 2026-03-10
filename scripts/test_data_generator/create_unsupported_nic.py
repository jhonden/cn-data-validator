#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""创建完全不支持的 NIC 包测试数据

这个包中的所有网元类型都不在 CNAE 支持列表中，
用于测试"无效 NIC 包"的校验规则。

预期结果:
- 状态：Invalid (红色)
- 提示：Invalid NIC package: No supported network elements found, no need to collect
"""

import os
import tarfile
import tempfile
import shutil


def create_unsupported_nic_package(output_path='test_data/test_unsupported_nic.tar.gz'):
    """创建完全不支持的 NIC 包

    Args:
        output_path: 输出文件路径
    """

    # 创建临时目录
    temp_dir = tempfile.mkdtemp(prefix='unsupported_nic_')
    print(f"Creating unsupported NIC package in: {temp_dir}")

    # 创建时间文件夹
    time_folder = "20250203105511"
    time_dir = os.path.join(temp_dir, time_folder)
    os.makedirs(time_dir, exist_ok=True)

    # 创建 neinfo.txt - 所有网元类型都不支持
    neinfo_path = os.path.join(time_dir, 'neinfo.txt')
    with open(neinfo_path, 'w', encoding='utf-8') as f:
        # 写入 5 个都不支持的网元实例
        f.write("PPR_UNSUP01   UNSUPPORTED_NE1=9999   56   10.140.2.1\n")
        f.write("PPR_UNSUP02   UNSUPPORTED_NE2=9998   57   10.140.2.2\n")
        f.write("PPR_UNSUP03   UNSUPPORTED_NE3=9997   58   10.140.2.3\n")
        f.write("PPR_UNSUP04   UNSUPPORTED_NE4=9996   59   10.140.2.4\n")
        f.write("PPR_UNSUP05   UNKNOWN_NE=9995   60   10.140.2.5\n")

    print("✓ Created neinfo.txt with 5 unsupported NE instances")

    # 为每个不支持的网元类型创建完整的数据文件夹
    ne_folders = {
        'UNSUPPORTED_NE1=9999_IP_10_140_2_1_56_PPR_UNSUP01': {
            'name': 'PPR_UNSUP01',
            'ne_type': 'UNSUPPORTED_NE1',
            'files': ['static_mml.txt', 'dynamic_mml.txt', 'statistics.txt']
        },
        'UNSUPPORTED_NE2=9998_IP_10_140_2_2_57_PPR_UNSUP02': {
            'name': 'PPR_UNSUP02',
            'ne_type': 'UNSUPPORTED_NE2',
            'files': ['static_mml.txt', 'dynamic_mml.txt', 'statistics.txt']
        },
        'UNSUPPORTED_NE3=9997_IP_10_140_2_3_58_PPR_UNSUP03': {
            'name': 'PPR_UNSUP03',
            'ne_type': 'UNSUPPORTED_NE3',
            'files': ['static_mml.txt', 'dynamic_mml.txt', 'statistics.txt']
        },
        'UNSUPPORTED_NE4=9996_IP_10_140_2_4_59_PPR_UNSUP04': {
            'name': 'PPR_UNSUP04',
            'ne_type': 'UNSUPPORTED_NE4',
            'files': ['static_mml.txt', 'dynamic_mml.txt', 'statistics.txt']
        },
        'UNKNOWN_NE=9995_IP_10_140_2_5_60_PPR_UNSUP05': {
            'name': 'PPR_UNSUP05',
            'ne_type': 'UNKNOWN_NE',
            'files': ['static_mml.txt', 'dynamic_mml.txt', 'statistics.txt']
        }
    }

    # 创建网元数据文件夹和文件
    for folder_name, folder_info in ne_folders.items():
        folder_path = os.path.join(time_dir, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        # 创建文件
        for file_name in folder_info['files']:
            file_path = os.path.join(folder_path, file_name)

            # 根据文件类型生成内容
            if 'static_mml' in file_name:
                content = f"""# Static MML Configuration for {folder_info['name']}
# Network Element: {folder_info['ne_type']}
# Instance ID: {folder_info['name']}

SET NE_NAME={folder_info['name']}
SET NE_TYPE={folder_info['ne_type']}
SET NE_GROUP=56
SET NE_IP=10.140.2.1

# Configuration parameters
SET PARAM1=value1
SET PARAM2=value2
"""
            elif 'dynamic_mml' in file_name:
                content = f"""# Dynamic MML Configuration for {folder_info['name']}
# Runtime configuration
# Generated at: 2025-02-03 10:55:11

MODIFY NE_STATE=ACTIVE
ADD ROUTE_TABLE=default

# Dynamic updates
UPDATE VERSION=1.0.0
"""
            elif 'statistics' in file_name:
                content = f"""# Statistics Data for {folder_info['name']}
# Collection Time: 2025-02-03 10:55:11

Total_Calls=12345
Success_Rate=99.5%
Error_Count=62

# Performance metrics
Avg_Response_Time=15ms
Max_Response_Time=45ms
"""
            else:
                content = f"# {file_name} content"

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

        print(f"✓ Created: {folder_name} ({folder_info['ne_type']}, complete)")

    # 创建 report 文件
    report_path = os.path.join(temp_dir, f'{time_folder}_report.tar.gz')
    with open(report_path, 'wb') as f:
        # 创建空的 report 文件
        f.write(b'\x1f\x8b\x08\x00\x00\x00\x00\x00\x00')  # gzip header
    print(f"✓ Created report file: {os.path.basename(report_path)}")

    # 确保输出目录存在
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)

    # 打包成 tar.gz
    with tarfile.open(output_path, 'w:gz') as tar:
        tar.add(time_dir, arcname=time_folder)
        tar.add(report_path, arcname=os.path.basename(report_path))

    print(f"\n✓ Test NIC package created: {output_path}")
    print(f"  File size: {os.path.getsize(output_path) / 1024:.2f} KB")

    # 清理临时目录
    shutil.rmtree(temp_dir, ignore_errors=True)
    print(f"✓ Cleaned up temporary directory")

    return output_path


if __name__ == '__main__':
    print("=" * 70)
    print("Create Unsupported NIC Package")
    print("=" * 70)
    print()
    print("This package contains ONLY unsupported network elements.")
    print("Expected validation result:")
    print("  Status: Invalid (Red)")
    print("  Message: Invalid NIC package: No supported network elements found, no need to collect")
    print()
    print("=" * 70)
    print()

    # 创建测试包
    output_file = create_unsupported_nic_package()

    print("\n" + "=" * 70)
    print("Next Steps:")
    print("=" * 70)
    print(f"\n1. Run validator: python3 validator_qt.py")
    print(f"2. Select the 'test_data' directory")
    print(f"3. Click 'Start Validation'")
    print(f"4. Look for 'test_unsupported_nic.tar.gz' in the table")
    print(f"5. Verify Status is 'Invalid' (Red)")
    print(f"6. Check Details column for the error message")
    print()
