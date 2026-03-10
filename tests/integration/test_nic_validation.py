#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试 NIC 包校验功能"""

import os
import sys
import tarfile
import tempfile
import shutil

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.service.nic_validator import NICValidator


def create_test_nic_package():
    """创建测试 NIC 包"""
    temp_dir = tempfile.mkdtemp(prefix='test_nic_')
    print(f"Creating test NIC package in: {temp_dir}")

    # 创建时间文件夹
    time_folder = "20250203105511"
    time_dir = os.path.join(temp_dir, time_folder)
    os.makedirs(time_dir, exist_ok=True)

    # 创建 neinfo.txt
    neinfo_path = os.path.join(time_dir, 'neinfo.txt')
    with open(neinfo_path, 'w', encoding='utf-8') as f:
        f.write("PPR_CSCF01   CSCF_NE=1094   56   10.140.2.1\n")
        f.write("PPR_ATS01   ATS_NE=1044   59   10.140.2.10\n")
        f.write("PPR_UDG01   UDG_NE=2001   10   10.140.3.5\n")
        # 添加不支持的网元类型
        f.write("PPR_UNSUPPORTED   UNKNOWN_NE=9999   99   10.140.4.1\n")

    print(f"✓ Created neinfo.txt with 4 NE instances")

    # 创建网元数据文件夹（故意不创建一个）
    ne_instances = [
        ('CSCF_NE=1094', '10.140.2.1', '56', 'PPR_CSCF01'),  # 正常，完整
        ('ATS_NE=1044', '10.140.2.10', '59', 'PPR_ATS01'),  # 缺少文件
        # UDG_NE=2001 的文件夹不创建（测试缺失文件夹）
    ]

    for ne_type_id, ip, group, name in ne_instances:
        ip_formatted = ip.replace('.', '_')
        folder_name = f"{ne_type_id}_IP_{ip_formatted}_{group}_{name}"
        folder_path = os.path.join(time_dir, folder_name)

        if ne_type_id == 'UDG_NE=2001':
            # 故意不创建这个文件夹
            print(f"✗ Skipping: {folder_name} (for testing missing folder)")
            continue

        os.makedirs(folder_path, exist_ok=True)

        # 创建一些文件
        if ne_type_id == 'CSCF_NE=1094':
            # 完整的文件
            with open(os.path.join(folder_path, 'static_mml.txt'), 'w') as f:
                f.write('Static MML config')
            with open(os.path.join(folder_path, 'dynamic_mml.txt'), 'w') as f:
                f.write('Dynamic MML config')
            with open(os.path.join(folder_path, 'statistics.txt'), 'w') as f:
                f.write('Statistics data')
            print(f"✓ Created: {folder_name} (with all files)")

        elif ne_type_id == 'ATS_NE=1044':
            # 缺少统计文件
            with open(os.path.join(folder_path, 'static_mml.txt'), 'w') as f:
                f.write('Static MML config')
            with open(os.path.join(folder_path, 'dynamic_mml.txt'), 'w') as f:
                f.write('Dynamic MML config')
            # 故意不创建 statistics.txt
            print(f"✓ Created: {folder_name} (missing statistics)")

    # 打包成 tar.gz
    nic_file = os.path.join(temp_dir, 'test_nic.tar.gz')
    with tarfile.open(nic_file, 'w:gz') as tar:
        tar.add(time_dir, arcname=time_folder)

    print(f"✓ Created test NIC package: {nic_file}")

    return temp_dir, nic_file


def test_nic_validation():
    """测试 NIC 校验功能"""
    print("=" * 60)
    print("Test: NIC Package Validation")
    print("=" * 60)
    print()

    # 创建测试包
    temp_dir, nic_file = create_test_nic_package()
    print()

    # 测试校验
    print("=" * 60)
    print("Test: Run Validation")
    print("=" * 60)

    validator = NICValidator(nic_file)
    result = validator.validate()

    print()
    print("Validation Results:")
    print(f"  Valid: {result.get('valid', False)}")
    print(f"  neinfo.txt exists: {result.get('neinfo_exists', False)}")
    print(f"  Total NE instances: {len(validator.ne_instances)}")
    print()

    # 显示不支持的网元类型
    unsupported = result.get('unsupported_types', [])
    if unsupported:
        print(f"Unsupported NE Types ({len(unsupported)}):")
        for ne in unsupported:
            print(f"  - {ne['name']}: {ne['ne_type']} (line {ne['line']})")
    else:
        print("✓ No unsupported NE types")
    print()

    # 显示缺失的文件夹
    missing_folders = result.get('missing_folders', [])
    if missing_folders:
        print(f"Missing NE Data Folders ({len(missing_folders)}):")
        for mf in missing_folders:
            print(f"  - {mf['name']} ({mf['ne_type']})")
            print(f"    Expected: {mf['expected_folder']}")
    else:
        print("✓ No missing NE data folders")
    print()

    # 显示缺失的文件
    missing_files = result.get('missing_files', {})
    if missing_files:
        print(f"Missing Key Files ({len(missing_files)} folders affected):")
        for folder, info in missing_files.items():
            print(f"  - {info['ne_name']} ({info['ne_type']})")
            for file in info['files']:
                print(f"    Missing: {file['description']} ({file['type']})")
    else:
        print("✓ No missing key files")
    print()

    # 显示警告和错误
    warnings = result.get('warnings', [])
    if warnings:
        print(f"Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"  - {w}")
    else:
        print("✓ No warnings")

    errors = result.get('errors', [])
    if errors:
        print(f"Errors ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
    else:
        print("✓ No errors")

    print()
    print("=" * 60)
    print("Test Complete!")
    print("=" * 60)

    # 清理
    shutil.rmtree(temp_dir, ignore_errors=True)
    print(f"✓ Cleaned up temporary directory")


if __name__ == '__main__':
    test_nic_validation()
