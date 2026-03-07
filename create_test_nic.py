#!/usr/bin/env python3
"""创建测试 NIC 包数据

生成包含不同情况的测试数据：
- 正常的网元（文件齐全）
- 缺少关键文件的网元
- 不支持的网元类型
"""

import os
import tarfile
import tempfile
import shutil


def create_test_nic_package(output_path='test_nic_package.tar.gz'):
    """创建测试 NIC 包

    Args:
        output_path: 输出文件名（相对或绝对路径），默认在当前目录
    """

    # 获取脚本所在目录作为输出目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_full_path = os.path.join(script_dir, output_path)

    # 临时目录用于构建包结构
    temp_dir = tempfile.mkdtemp(prefix='test_nic_creation_')
    print(f"Creating test NIC package in: {temp_dir}")
    print(f"Will output to: {output_full_path}")
    print()

    # 创建时间文件夹
    time_folder = "20250203105511"
    time_dir = os.path.join(temp_dir, time_folder)
    os.makedirs(time_dir, exist_ok=True)

    # 创建 neinfo.txt
    neinfo_path = os.path.join(time_dir, 'neinfo.txt')
    with open(neinfo_path, 'w', encoding='utf-8') as f:
        # 写入网元实例信息
        f.write("PPR_CSCF01   CSCF_NE=1094   56   10.140.2.1\n")    # 正常，文件齐全
        f.write("PPR_ATS01   ATS_NE=1044   59   10.140.2.10\n")     # 缺少话统文件
        f.write("PPR_UDG01   UDG_NE=2001   10   10.140.3.5\n")      # 缺少网元数据文件夹
        f.write("PPR_CCFC01   CCF_NE=1095   56   10.140.2.2\n")    # 缺少静态MML文件
        f.write("PPR_USC01   USC_NE=1096   57   10.140.2.3\n")     # 缺少动态MML文件
        f.write("PPR_SPSV01   SPSV3_NE=1097   58   10.140.2.4\n")  # 缺少所有关键文件
        f.write("PPR_CGP01   CGPOMU_NE=1098   59   10.140.2.5\n")   # 缺少话统和动态MML
        f.write("PPR_UNSUP01   UNSUPPORTED_NE=9999   99   10.140.4.1\n") # 不支持的网元类型

    print("✓ Created neinfo.txt with 8 NE instances")

    # 定义网元数据文件夹及其文件情况
    ne_folders = {
        # 完整的网元（所有文件都在）
        'CSCF_NE=1094_IP_10_140_2_1_56_PPR_CSCF01': {
            'name': 'PPR_CSCF01',
            'ne_type': 'CSCF',
            'files': ['static_mml.txt', 'dynamic_mml.txt', 'statistics.txt']
        },

        # 缺少话统文件
        'ATS_NE=1044_IP_10_140_2_10_59_PPR_ATS01': {
            'name': 'PPR_ATS01',
            'ne_type': 'ATS',
            'files': ['static_mml.txt', 'dynamic_mml.txt']  # 缺少 statistics.txt
        },

        # 缺少静态MML文件
        'CCF_NE=1095_IP_10_140_2_2_56_PPR_CCFC01': {
            'name': 'PPR_CCFC01',
            'ne_type': 'CCF',
            'files': ['dynamic_mml.txt', 'statistics.txt']  # 缺少 static_mml.txt
        },

        # 缺少动态MML文件
        'USC_NE=1096_IP_10_140_2_3_57_PPR_USC01': {
            'name': 'PPR_USC01',
            'ne_type': 'USC',
            'files': ['static_mml.txt', 'statistics.txt']  # 缺少 dynamic_mml.txt
        },

        # 缺少所有关键文件
        'SPSV3_NE=1097_IP_10_140_2_4_58_PPR_SPSV01': {
            'name': 'PPR_SPSV01',
            'ne_type': 'SPSV3',
            'files': []  # 所有关键文件都缺失
        },

        # 缺少话统和动态MML
        'CGPOMU_NE=1098_IP_10_140_2_5_59_PPR_CGP01': {
            'name': 'PPR_CGP01',
            'ne_type': 'CGPOMU',
            'files': ['static_mml.txt']  # 只有静态MML
        },

        # 不支持的网元类型 - 也要创建文件夹
        'UNSUPPORTED_NE=9999_IP_10_140_4_1_99_PPR_UNSUP01': {
            'name': 'PPR_UNSUP01',
            'ne_type': 'UNSUPPORTED',
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
# Instance ID: NE=1094

SET NE_NAME={folder_info['name']}
SET NE_TYPE={folder_info['ne_type']}
SET NE_GROUP=56
SET NE_IP=10.140.2.1
"""
            elif 'dynamic_mml' in file_name:
                content = f"""# Dynamic MML Configuration for {folder_info['name']}
# Runtime configuration
# Generated at: 2025-02-03 10:55:11

MODIFY NE_STATE=ACTIVE
ADD ROUTE_TABLE=default
"""
            elif 'statistics' in file_name:
                content = f"""# Statistics Data for {folder_info['name']}
# Collection Time: 2025-02-03 10:55:11

Total_Calls=12345
Success_Rate=99.5%
Error_Count=62
"""
            else:
                content = f"# {file_name} content"

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

        file_status = "complete" if len(folder_info['files']) == 3 else f"{len(folder_info['files'])} files"
        print(f"✓ Created: {folder_name} ({folder_info['ne_type']}, {file_status})")

    # 创建 report 文件（模拟真实NIC包）
    report_path = os.path.join(temp_dir, f'{time_folder}_report.tar.gz')
    with open(report_path, 'wb') as f:
        # 创建空的 report 文件
        f.write(b'\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\x00')  # gzip header
    print(f"✓ Created report file: {os.path.basename(report_path)}")

    # 打包成 tar.gz - 输出到脚本所在目录
    output_file = output_full_path
    with tarfile.open(output_file, 'w:gz') as tar:
        tar.add(time_dir, arcname=time_folder)
        tar.add(report_path, arcname=os.path.basename(report_path))

    print(f"\n✓ Test NIC package created: {output_file}")
    print(f"  File size: {os.path.getsize(output_file) / 1024:.2f} KB")

    # 清理临时目录
    shutil.rmtree(temp_dir, ignore_errors=True)
    print(f"✓ Cleaned up temporary directory")

    return output_file


def print_summary():
    """打印测试数据摘要"""
    print("\n" + "=" * 70)
    print("Test NIC Package Summary")
    print("=" * 70)
    print("\nTest Data Scenarios:")
    print()

    scenarios = [
        ("1. PPR_CSCF01 (CSCF)", "Complete - All files present"),
        ("2. PPR_ATS01 (ATS)", "Missing - statistics file"),
        ("3. PPR_UDG01 (UDG)", "Missing - Data folder not created"),
        ("4. PPR_CCFC01 (CCF)", "Missing - static_mml file"),
        ("5. PPR_USC01 (USC)", "Missing - dynamic_mml file"),
        ("6. PPR_SPSV01 (SPSV3)", "Missing - All key files"),
        ("7. PPR_CGP01 (CGPOMU)", "Missing - statistics & dynamic_mml"),
        ("8. PPR_UNSUP01 (UNSUPPORTED)", "Unsupported NE type"),
    ]

    for scenario, description in scenarios:
        print(f"  {scenario}")
        print(f"    └─ {description}")

    print("\n" + "=" * 70)
    print("Expected Validation Results:")
    print("=" * 70)
    print("\n✓ Should detect:")
    print("  - 1 unsupported NE type (UNSUPPORTED)")
    print("  - 1 missing NE data folder (UDG)")
    print("  - 6 missing key files across 5 NE instances")
    print("  - Validation status: Warning (orange)")
    print()


if __name__ == '__main__':
    print("=" * 70)
    print("Create Test NIC Package")
    print("=" * 70)
    print()

    # 打印测试摘要
    print_summary()

    # 创建测试包
    output_file = create_test_nic_package('test_nic_package.tar.gz')

    print("\n" + "=" * 70)
    print("Next Steps:")
    print("=" * 70)
    print(f"\n1. Run validator: python3 validator_qt.py")
    print(f"2. Select the directory containing: {os.path.basename(output_file)}")
    print(f"3. Click 'Start Validation'")
    print(f"4. Check validation results in the table")
    print(f"5. Look for 'Warning' status in the 'Details' column")
    print()
