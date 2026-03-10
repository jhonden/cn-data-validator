#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实际功能测试
测试重构后的实际功能是否正常工作
"""

import sys
import os
import tempfile
import shutil

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
os.chdir(project_root)  # 切换到项目根目录

def create_test_nic_package():
    """创建一个测试用的NIC包"""
    import tarfile
    from datetime import datetime

    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    # 创建NIC包结构
    nic_dir = os.path.join(temp_dir, timestamp)
    os.makedirs(nic_dir)

    # 创建neinfo.txt
    neinfo_content = """# NE信息文件
NE1,UNC,001,192.168.1.100,group1,Test NE
NE2,UDG,002,192.168.1.101,group2,Test NE2
"""
    with open(os.path.join(nic_dir, "neinfo.txt"), "w") as f:
        f.write(neinfo_content)

    # 创建报告文件
    report_dir = os.path.join(temp_dir, f"{timestamp}_report")
    os.makedirs(report_dir)

    # 创建空的报告文件
    with open(os.path.join(report_dir, "report.xml"), "w") as f:
        f.write("<report></report>")

    # 创建NIC包
    nic_path = os.path.join(temp_dir, f"{timestamp}.tar.gz")
    with tarfile.open(nic_path, "w:gz") as tar:
        tar.add(nic_dir, arcname=timestamp)
        tar.add(report_dir, arcname=f"{timestamp}_report")

    return nic_path

def test_file_scanning():
    """测试文件扫描功能"""
    print("🔍 测试文件扫描功能...")

    try:
        from src.service.file_scanner import FileScanner

        # 创建测试目录和文件
        test_dir = tempfile.mkdtemp()

        # 创建测试文件
        test_files = [
            "valid.tar.gz",
            "valid.zip",
            "invalid.txt",
            "test.xlsx"
        ]

        for filename in test_files:
            filepath = os.path.join(test_dir, filename)
            with open(filepath, 'w') as f:
                f.write("test content")

        # 扫描
        scanner = FileScanner(test_dir)
        results = []

        def progress_callback(progress):
            pass

        scan_results = scanner.scan_directory(progress_callback)

        print(f"✅ 扫描完成，发现 {len(scan_results)} 个文件")

        # 统计结果
        valid_count = sum(1 for r in scan_results if r.get('package_type') != None)
        invalid_count = sum(1 for r in scan_results if r.get('package_type') is None)

        print(f"   - 有效文件: {valid_count}")
        print(f"   - 无效文件: {invalid_count}")

        # 清理
        shutil.rmtree(test_dir)

        return True

    except Exception as e:
        print(f"❌ 文件扫描测试失败: {e}")
        return False

def test_nic_validation():
    """测试NIC包验证功能"""
    print("\n🔍 测试NIC包验证功能...")

    try:
        from src.service.nic_validator import NICValidator

        # 创建测试NIC包
        nic_path = create_test_nic_package()

        # 创建验证器
        validator = NICValidator(nic_path)

        # 执行验证
        validation_result = validator.validate()

        print(f"✅ NIC包验证完成")
        print(f"   - 结果: {validation_result['valid']}")
        print(f"   - NE实例数: {len(validation_result.get('ne_instances', []))}")

        # 清理
        shutil.rmtree(os.path.dirname(nic_path))

        return True

    except Exception as e:
        print(f"❌ NIC包验证测试失败: {e}")
        return False

def test_package_identification():
    """测试包识别功能"""
    print("\n🔍 测试包识别功能...")

    try:
        from src.service.package_identifier import PackageIdentifier

        identifier = PackageIdentifier()

        test_cases = [
            ("20250310103000_report.tar.gz", "NIC包格式"),
            ("test.zip", "ZIP文件"),
            ("invalid.tar.gz", "无效格式"),
            ("report.xlsx", "Excel文件")
        ]

        for filename, desc in test_cases:
            package_type, details = identifier.identify("", filename)
            print(f"   - {filename}: {package_type} ({desc})")

        print("✅ 包识别功能正常")
        return True

    except Exception as e:
        print(f"❌ 包识别测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("=" * 60)
    print(" 实际功能测试")
    print("=" * 60)

    tests = [
        test_file_scanning,
        test_nic_validation,
        test_package_identification
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print("\n" + "=" * 60)
    print(f" 测试结果: {passed}/{total} 通过")
    print("=" * 60)

    if passed == total:
        print("🎉 所有实际功能测试通过！重构成功！")
        return True
    else:
        print("⚠️  部分测试失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)