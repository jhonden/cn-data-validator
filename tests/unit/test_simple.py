#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试所有版本的导入 - Simple version
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

def test_imports():
    print("Starting import tests...\n")

    # Test core module
    print("1. Testing core module...")
    try:
        from src.service.file_scanner import FileScanner
        print("   [OK] FileScanner import successful")
    except Exception as e:
        print(f"   [FAIL] FileScanner import failed: {e}")
        return False

    # Test CLI version dependencies
    print("\n2. Testing CLI version dependencies...")
    try:
        import os, sys, traceback, datetime, csv
        print("   [OK] CLI version dependencies import successful")
    except Exception as e:
        print(f"   [FAIL] CLI version dependencies import failed: {e}")
        return False

    # Test CustomTkinter GUI version dependencies
    print("\n3. Testing CustomTkinter GUI version dependencies...")
    try:
        import tkinter
        import customtkinter as ctk
        print("   [OK] CustomTkinter import successful")
    except Exception as e:
        print(f"   [FAIL] CustomTkinter import failed: {e}")
        print("   Note: GUI version may not be available")

    # Test PySimpleGUI GUI version dependencies
    print("\n4. Testing PySimpleGUI GUI version dependencies...")
    try:
        import PySimpleGUI as sg
        print("   [OK] PySimpleGUI import successful")
    except Exception as e:
        print(f"   [FAIL] PySimpleGUI import failed: {e}")
        print("   Note: PySimpleGUI version may not be available")

    # Test PyQt6 GUI version dependencies
    print("\n5. Testing PyQt6 GUI version dependencies...")
    try:
        from PyQt6.QtWidgets import QApplication
        print("   [OK] PyQt6 import successful")
    except Exception as e:
        print(f"   [FAIL] PyQt6 import failed: {e}")
        print("   Note: PyQt6 version may not be available")

    print("\nTests completed!")
    print("\nRecommendations:")
    print("- CLI version should work normally")
    print("- Choose available GUI version based on test results")

    return True

if __name__ == "__main__":
    test_imports()
