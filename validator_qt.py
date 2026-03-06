#!/usr/bin/env python3
"""
网络数据包校验工具 - PyQt6 GUI版本
使用 PyQt6 实现，不依赖 tkinter，有更好的跨平台兼容性
"""

import sys
import os
import traceback
from datetime import datetime

# 添加当前目录到sys.path以支持模块导入
if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QProgressBar, QStatusBar, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from utils.file_scanner import FileScanner


class ValidationThread(QThread):
    """校验线程，避免阻塞 UI"""
    finished = pyqtSignal(object, str)
    progress = pyqtSignal(int)

    def __init__(self, directory):
        super().__init__()
        self.directory = directory

    def run(self):
        try:
            scanner = FileScanner(self.directory)
            scanner.scan_directory()
            self.finished.emit(scanner, "")
        except Exception as e:
            self.finished.emit(None, str(e))


class ValidatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_dir = ""
        self.validation_thread = None
        self.scanner = None

        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("网络数据包校验工具")
        self.setGeometry(100, 100, 1200, 700)

        # 主窗口
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # 主布局
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # 顶部控制区
        control_layout = QHBoxLayout()

        self.dir_label = QLabel("请选择数据包目录:")
        self.dir_label.setFont(QFont("Arial", 10))
        control_layout.addWidget(self.dir_label)

        self.dir_path_label = QLabel("")
        self.dir_path_label.setStyleSheet("color: #666; font-style: italic;")
        self.dir_path_label.setMinimumWidth(400)
        control_layout.addWidget(self.dir_path_label)

        self.select_btn = QPushButton("选择目录")
        self.select_btn.setFixedWidth(120)
        self.select_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.select_btn.clicked.connect(self.select_directory)
        control_layout.addWidget(self.select_btn)

        self.validate_btn = QPushButton("开始校验")
        self.validate_btn.setFixedWidth(120)
        self.validate_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.validate_btn.clicked.connect(self.start_validation)
        self.validate_btn.setEnabled(False)
        control_layout.addWidget(self.validate_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(200)
        self.progress_bar.setVisible(False)
        control_layout.addWidget(self.progress_bar)

        control_layout.addStretch()
        layout.addLayout(control_layout)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["文件名", "文件路径", "大小", "格式", "包类型", "状态", "详情"])

        # 设置列宽
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)

        # 设置表格样式
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)

        layout.addWidget(self.table)

        # 底部按钮区
        button_layout = QHBoxLayout()

        self.export_btn = QPushButton("导出结果")
        self.export_btn.setFixedWidth(120)
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        self.export_btn.clicked.connect(self.export_results)
        self.export_btn.setEnabled(False)
        button_layout.addWidget(self.export_btn)

        button_layout.addStretch()

        self.stats_label = QLabel("准备就绪")
        button_layout.addWidget(self.stats_label)

        layout.addLayout(button_layout)

        # 状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

    def select_directory(self):
        """选择目录"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择数据包目录",
            "",
            QFileDialog.Option.ShowDirsOnly
        )

        if directory:
            self.current_dir = directory
            self.dir_path_label.setText(f"已选择: {os.path.basename(directory)}")
            self.validate_btn.setEnabled(True)
            self.statusBar.showMessage(f"已选择目录: {directory}")

    def start_validation(self):
        """开始校验"""
        if not self.current_dir:
            QMessageBox.warning(self, "警告", "请先选择数据包目录")
            return

        # 清空表格
        self.table.setRowCount(0)
        self.stats_label.setText("正在扫描...")
        self.validate_btn.setEnabled(False)
        self.select_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # 启动校验线程
        self.validation_thread = ValidationThread(self.current_dir)
        self.validation_thread.finished.connect(self.on_validation_finished)
        self.validation_thread.progress.connect(self.update_progress)
        self.validation_thread.start()

    def update_progress(self, value):
        """更新进度"""
        self.progress_bar.setValue(value)

    def on_validation_finished(self, scanner, error):
        """校验完成"""
        self.validate_btn.setEnabled(True)
        self.select_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

        if error:
            QMessageBox.critical(self, "错误", f"校验过程中发生错误:\n{error}")
            self.stats_label.setText("校验失败")
            return

        self.scanner = scanner
        self.display_results()

    def display_results(self):
        """显示结果"""
        stats = self.scanner.get_statistics()

        # 显示合法文件
        for file_info in self.scanner.valid_files:
            # 获取包类型和详情
            package_type = file_info.get('package_type', '未知')
            package_details = file_info.get('package_details', {})

            # 根据包类型设置颜色
            if package_type == 'NIC包':
                package_color = '#2196F3'  # 蓝色
            elif package_type == '未知':
                package_color = '#FF9800'  # 橙色
            else:
                package_color = '#666666'  # 灰色

            # 生成详情信息
            detail = ''
            if package_type == 'NIC包':
                time = package_details.get('time', '')
                if time:
                    detail = f'时间: {time}'
            elif package_type == '未知':
                note = package_details.get('note', '')
                if note:
                    detail = note

            self.add_file_row(
                file_info['name'],
                file_info['relative_path'],
                self._format_size(file_info['size']),
                self._get_file_type(file_info['name']),
                package_type,
                '✅ 合法',
                detail,
                '#4CAF50',  # 状态颜色（绿色）
                package_color  # 包类型颜色
            )

        # 显示非法文件
        for file_info in self.scanner.illegal_files:
            self.add_file_row(
                file_info['name'],
                file_info['relative_path'],
                self._format_size(file_info['size']),
                self._get_file_type(file_info['name']),
                '-',
                '❌ 非法',
                '数据包格式非法',
                '#F44336',  # 状态颜色（红色）
                '#666666'  # 包类型颜色（灰色）
            )

        # 更新统计信息
        self.stats_label.setText(
            f"总计: {stats['total_files']} 个文件 | "
            f"合法: {stats['valid_files']} | "
            f"非法: {stats['illegal_files']}"
        )

        self.statusBar.showMessage(f"扫描完成: 共找到 {stats['total_files']} 个文件")
        self.export_btn.setEnabled(True)

        # 显示提示
        if stats['illegal_files'] > 0:
            QMessageBox.warning(
                self,
                "扫描完成",
                f"扫描完成！\n\n"
                f"总文件数: {stats['total_files']}\n"
                f"合法文件: {stats['valid_files']}\n"
                f"非法文件: {stats['illegal_files']}\n\n"
                f"请检查表格中的非法文件。"
            )
        else:
            QMessageBox.information(
                self,
                "扫描完成",
                f"扫描完成！\n\n"
                f"所有 {stats['total_files']} 个文件格式均合法。"
            )

    def add_file_row(self, name, path, size, file_type, package_type, status, detail, status_color, package_color):
        """添加文件行到表格"""
        row = self.table.rowCount()
        self.table.insertRow(row)

        items = [name, path, size, file_type, package_type, status, detail]

        for col, item_text in enumerate(items):
            item = QTableWidgetItem(str(item_text))
            # 状态列（第5列）使用状态颜色
            if col == 5:
                item.setForeground(QColor(status_color))
                item.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            # 包类型列（第4列）使用包类型颜色
            elif col == 4:
                item.setForeground(QColor(package_color))
                item.setFont(QFont("Arial", 9))
            self.table.setItem(row, col, item)

    def _format_size(self, size):
        """格式化文件大小"""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size/1024:.1f} KB"
        else:
            return f"{size/(1024*1024):.1f} MB"

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

    def export_results(self):
        """导出结果"""
        if not self.scanner:
            QMessageBox.warning(self, "警告", "没有可导出的结果")
            return

        # 选择保存文件
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存结果",
            f"校验结果_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "文本文件 (*.txt);;CSV文件 (*.csv);;所有文件 (*.*)"
        )

        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self._export_csv(file_path)
                else:
                    self._export_txt(file_path)

                QMessageBox.information(self, "成功", f"结果已导出到:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败:\n{str(e)}")

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
            stats = self.scanner.get_statistics()
            if stats:
                f.write(f"统计信息:\n")
                f.write(f"  总文件数: {stats['total_files']}\n")
                f.write(f"  合法文件: {stats['valid_files']}\n")
                f.write(f"  非法文件: {stats['illegal_files']}\n")
                f.write("\n")

            # 详细结果
            f.write("详细结果:\n")
            f.write("-" * 50 + "\n")

            for row in range(self.table.rowCount()):
                f.write(f"文件名: {self.table.item(row, 0).text()}\n")
                f.write(f"路径: {self.table.item(row, 1).text()}\n")
                f.write(f"大小: {self.table.item(row, 2).text()}\n")
                f.write(f"格式: {self.table.item(row, 3).text()}\n")
                f.write(f"包类型: {self.table.item(row, 4).text()}\n")
                f.write(f"状态: {self.table.item(row, 5).text()}\n")
                detail = self.table.item(row, 6).text()
                if detail:
                    f.write(f"详情: {detail}\n")
                f.write("\n")

    def _export_csv(self, filename):
        """导出为CSV文件"""
        import csv

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['文件名', '文件路径', '大小', '格式', '包类型', '状态', '详情'])

            for row in range(self.table.rowCount()):
                writer.writerow([
                    self.table.item(row, 0).text(),
                    self.table.item(row, 1).text(),
                    self.table.item(row, 2).text(),
                    self.table.item(row, 3).text(),
                    self.table.item(row, 4).text(),
                    self.table.item(row, 5).text(),
                    self.table.item(row, 6).text()
                ])


def main():
    app = QApplication(sys.argv)

    # 设置应用样式
    app.setStyle("Fusion")

    window = ValidatorApp()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
