#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络数据包校验工具 - 命令行版本
适用于无法使用 GUI 的环境
"""

import os
import sys
import traceback
from datetime import datetime

# 添加当前目录到sys.path以支持模块导入
if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.file_scanner import FileScanner

class ValidatorCLI:
    def __init__(self):
        self.current_dir = ""
        self.scanner = None
        self.validation_results = []

    def run(self):
        """运行命令行界面"""
        print("=" * 60)
        print(" 网络数据包校验工具 - 命令行版本".center(60))
        print("=" * 60)
        print()

        # 获取数据包目录
        while True:
            print("请选择数据包目录（输入 'q' 退出）：")
            print("请输入目录路径:")
            print("提示：可以拖拽文件夹到终端窗口自动粘贴路径")
            print()

            self.current_dir = input("目录路径: ").strip()

            if self.current_dir.lower() == 'q':
                print("退出程序。")
                return

            if os.path.isdir(self.current_dir):
                print(f"已选择目录: {self.current_dir}\n")
                break
            else:
                print(f"错误: 目录不存在: {self.current_dir}\n")
                print("请检查路径是否正确，或按 q 退出程序\n")

        if not self.current_dir:
            print("退出程序。")
            return

        # 执行校验
        print(f"\n正在扫描目录: {self.current_dir}")
        print("-" * 60)

        try:
            self.validate_all()
        except Exception as e:
            print(f"错误: {str(e)}")
            traceback.print_exc()

        # 导出结果
        while True:
            print()
            choice = input("是否导出结果？(y/n/q): ").strip().lower()
            if choice == 'y':
                self.export_results()
                break
            elif choice == 'n':
                break
            elif choice == 'q':
                print("退出程序。")
                return

        print("\n校验完成！")

    def validate_all(self):
        """开始校验"""
        # 扫描目录
        self.scanner = FileScanner(self.current_dir)
        self.scanner.scan_directory()

        # 获取统计
        stats = self.scanner.get_statistics()

        # 显示统计信息
        print(f"\n扫描完成！")
        print(f"  总文件数: {stats['total_files']}")
        print(f"  合法文件: {stats['valid_files']}")
        print(f"  非法文件: {stats['illegal_files']}")
        print()

        # 显示非法文件
        if self.scanner.illegal_files:
            print("非法文件列表:")
            print("-" * 60)
            for i, file_info in enumerate(self.scanner.illegal_files, 1):
                print(f"{i}. {file_info['name']}")
                print(f"   路径: {file_info['relative_path']}")
                print(f"   大小: {self._format_size(file_info['size'])}")
                print(f"   原因: 数据包格式非法")
                print()

        # 显示合法文件（简要）
        if self.scanner.valid_files:
            print(f"合法文件: {len(self.scanner.valid_files)} 个")
            print()

    def _format_size(self, size):
        """格式化文件大小"""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size/1024:.1f} KB"
        else:
            return f"{size/(1024*1024):.1f} MB"

    def export_results(self):
        """导出结果"""
        # 选择导出格式
        print("\n导出格式:")
        print("  1. TXT 文本格式")
        print("  2. CSV 表格格式")

        choice = input("请选择 (1/2): ").strip()

        if choice == '1':
            ext = '.txt'
        elif choice == '2':
            ext = '.csv'
        else:
            print("无效选择，导出为 TXT 格式。")
            ext = '.txt'

        # 获取保存路径
        default_name = f"校验结果_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        save_path = input(f"\n请输入保存路径（直接回车使用默认: {default_name}）: ").strip()

        if not save_path:
            save_path = default_name

        try:
            if ext == '.csv':
                self._export_csv(save_path)
            else:
                self._export_txt(save_path)

            print(f"\n✓ 结果已导出到: {os.path.abspath(save_path)}")
        except Exception as e:
            print(f"\n✗ 导出失败: {str(e)}")

    def _export_txt(self, filename):
        """导出为文本文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("网络数据包校验结果\n")
            f.write("=" * 50 + "\n")
            f.write(f"校验时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"数据包目录: {self.current_dir}\n")
            f.write(f"支持格式: ZIP, TAR.GZ, TAR, XLSX\n")
            f.write("\n")

            # 统计信息
            stats = self.scanner.get_statistics() if self.scanner else None
            if stats:
                f.write(f"统计信息:\n")
                f.write(f"  总文件数: {stats['total_files']}\n")
                f.write(f"  合法文件: {stats['valid_files']}\n")
                f.write(f"  非法文件: {stats['illegal_files']}\n")
                f.write("\n")

            # 非法文件详情
            if self.scanner and self.scanner.illegal_files:
                f.write("非法文件:\n")
                f.write("-" * 50 + "\n")
                for file_info in self.scanner.illegal_files:
                    f.write(f"文件名: {file_info['name']}\n")
                    f.write(f"路径: {file_info['relative_path']}\n")
                    f.write(f"大小: {self._format_size(file_info['size'])}\n")
                    f.write(f"原因: 数据包格式非法\n")
                    f.write("\n")

            # 合法文件列表
            if self.scanner and self.scanner.valid_files:
                f.write("合法文件:\n")
                f.write("-" * 50 + "\n")
                for file_info in self.scanner.valid_files:
                    f.write(f"  - {file_info['name']}\n")
                f.write("\n")

    def _export_csv(self, filename):
        """导出为CSV文件"""
        import csv

        columns = ['文件名', '文件路径', '大小', '格式', '状态', '详情']

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(columns)

            # 合法文件
            if self.scanner and self.scanner.valid_files:
                for file_info in self.scanner.valid_files:
                    writer.writerow([
                        file_info['name'],
                        file_info['relative_path'],
                        self._format_size(file_info['size']),
                        self._get_file_type(file_info['name']),
                        '✅ 合法',
                        ''
                    ])

            # 非法文件
            if self.scanner and self.scanner.illegal_files:
                for file_info in self.scanner.illegal_files:
                    writer.writerow([
                        file_info['name'],
                        file_info['relative_path'],
                        self._format_size(file_info['size']),
                        self._get_file_type(file_info['name']),
                        '❌ 非法',
                        '数据包格式非法'
                    ])

    def _get_file_type(self, filename):
        """获取文件类型"""
        if filename.endswith('.zip'):
            return 'ZIP'
        elif filename.endswith('.tar.gz'):
            return 'TAR.GZ'
        elif filename.endswith('.tar'):
            return 'TAR'
        elif filename.endswith('.xlsx'):
            return 'XLSX'
        else:
            return '未知'

if __name__ == "__main__":
    app = ValidatorCLI()
    app.run()
