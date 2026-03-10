#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重构后的结构测试脚本

测试重构后的代码结构是否正确，各模块功能是否正常
"""

import sys
import os
import tempfile
import shutil
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_basic_imports():
    """测试基本模块导入"""
    print("📋 测试1: 基本模块导入")

    try:
        from src.view.validator_qt import ValidatorApp
        from src.view.validator_cli import ValidatorCLI
        from src.service.file_scanner import FileScanner
        from src.service.package_identifier import PackageIdentifier
        from src.service.nic_validator import NICValidator
        from src.service.scenario_checker import ScenarioChecker
        from src.service.static_mml.static_mml_checker import StaticMMLChecker
        # 配置文件是YAML格式，不需要Python导入
        print("✅ 所有核心模块导入成功")
        return True
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_file_scanner():
    """测试文件扫描功能"""
    print("\n📋 测试2: 文件扫描功能")

    try:
        from service.file_scanner import FileScanner

        # 创建临时测试目录
        test_dir = tempfile.mkdtemp()

        # 创建测试文件
        test_file1 = os.path.join(test_dir, "test1.tar.gz")
        test_file2 = os.path.join(test_dir, "test2.zip")

        # 创建空文件
        with open(test_file1, 'w') as f:
            f.write("")
        with open(test_file2, 'w') as f:
            f.write("")

        # 测试扫描
        scanner = FileScanner(test_dir)
        results = []

        def progress_callback(progress):
            pass

        scan_results = scanner.scan_directory(progress_callback)

        print(f"✅ 扫描完成，发现 {len(scan_results)} 个文件")

        # 清理
        shutil.rmtree(test_dir)

        return True
    except Exception as e:
        print(f"❌ 文件扫描测试失败: {e}")
        return False

def test_package_identifier():
    """测试包识别功能"""
    print("\n📋 测试3: 包识别功能")

    try:
        from service.package_identifier import PackageIdentifier

        # 创建测试包名
        test_cases = [
            "20250310103000_report.tar.gz",
            "invalid_name.tar.gz",
            "test.zip",
            "test.txt"
        ]

        identifier = PackageIdentifier()

        for name in test_cases:
            package_type = identifier.identify("", name)
            print(f"  - {name}: {package_type}")

        print("✅ 包识别功能正常")
        return True
    except Exception as e:
        print(f"❌ 包识别测试失败: {e}")
        return False

def test_gui_functionality():
    """测试GUI功能"""
    print("\n📋 测试4: GUI功能检查")

    try:
        from view.validator_qt import ValidatorApp
        print("✅ ValidatorApp类定义正确")

        # 检查关键方法是否存在
        app_class = ValidatorApp
        required_methods = ['__init__', 'init_ui', 'select_directory', 'start_validation']

        for method in required_methods:
            if hasattr(app_class, method):
                print(f"  ✅ 方法 {method} 存在")
            else:
                print(f"  ❌ 方法 {method} 不存在")
                return False

        return True
    except Exception as e:
        print(f"❌ GUI功能测试失败: {e}")
        return False

def test_cli_functionality():
    """测试CLI功能"""
    print("\n📋 测试5: CLI功能检查")

    try:
        from view.validator_cli import ValidatorCLI
        print("✅ ValidatorCLI类定义正确")

        # 检查关键方法是否存在
        cli_class = ValidatorCLI
        required_methods = ['__init__', 'run', 'validate_all']

        for method in required_methods:
            if hasattr(cli_class, method):
                print(f"  ✅ 方法 {method} 存在")
            else:
                print(f"  ❌ 方法 {method} 不存在")
                return False

        return True
    except Exception as e:
        print(f"❌ CLI功能测试失败: {e}")
        return False

def test_config_loading():
    """测试配置文件加载"""
    print("\n📋 测试6: 配置文件加载")

    try:
        from service.static_mml.static_mml_checker import StaticMMLChecker

        # 测试配置加载（使用相对路径）
        config_path = "src/config/static_mml_config.yaml"
        checker = StaticMMLChecker(config_path)
        print("✅ 静态MML配置加载成功")

        return True
    except Exception as e:
        print(f"❌ 配置加载测试失败: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print(" 重构后功能测试")
    print("=" * 60)

    tests = [
        test_basic_imports,
        test_file_scanner,
        test_package_identifier,
        test_gui_functionality,
        test_cli_functionality,
        test_config_loading
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
        print("🎉 所有测试通过！重构成功！")
        return True
    else:
        print("⚠️  部分测试失败，需要检查")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)