#!/usr/bin/env python3
"""
Network Package Validator - PyQt6 GUI Version
A local tool for validating network data collection results.
Helps users quickly identify issues with invalid file formats and missing files.

Implemented using PyQt6 for better cross-platform compatibility (no tkinter dependency).
"""

import sys
import os
import traceback
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QProgressBar, QStatusBar, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from utils.file_scanner import FileScanner


class ValidationThread(QThread):
    """Validation thread to avoid blocking UI"""
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
        """Initialize UI"""
        self.setWindowTitle("Network Package Validator")
        self.setGeometry(100, 100, 1200, 700)

        # Main window
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Main layout
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Top control area
        control_layout = QHBoxLayout()

        self.dir_label = QLabel("Select Package Directory:")
        self.dir_label.setFont(QFont("Arial", 10))
        control_layout.addWidget(self.dir_label)

        self.dir_path_label = QLabel("")
        self.dir_path_label.setStyleSheet("color: #666; font-style: italic;")
        self.dir_path_label.setMinimumWidth(400)
        control_layout.addWidget(self.dir_path_label)

        self.select_btn = QPushButton("Select Directory")
        self.select_btn.setFixedWidth(140)
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

        self.validate_btn = QPushButton("Start Validation")
        self.validate_btn.setFixedWidth(140)
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

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Filename", "Path", "Size", "Format", "Package Type", "Status", "Details"])

        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)

        # Set table style
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)

        layout.addWidget(self.table)

        # Bottom button area
        button_layout = QHBoxLayout()

        self.export_btn = QPushButton("Export Results")
        self.export_btn.setFixedWidth(140)
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

        self.stats_label = QLabel("Ready")
        button_layout.addWidget(self.stats_label)

        layout.addLayout(button_layout)

        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

    def select_directory(self):
        """Select directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Package Directory",
            "",
            QFileDialog.Option.ShowDirsOnly
        )

        if directory:
            self.current_dir = directory
            self.dir_path_label.setText(f"Selected: {os.path.basename(directory)}")
            self.validate_btn.setEnabled(True)
            self.statusBar.showMessage(f"Selected directory: {directory}")

    def start_validation(self):
        """Start validation"""
        if not self.current_dir:
            QMessageBox.warning(self, "Warning", "Please select a data package directory first")
            return

        # Clear table
        self.table.setRowCount(0)
        self.stats_label.setText("Scanning...")
        self.validate_btn.setEnabled(False)
        self.select_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Start validation thread
        self.validation_thread = ValidationThread(self.current_dir)
        self.validation_thread.finished.connect(self.on_validation_finished)
        self.validation_thread.progress.connect(self.update_progress)
        self.validation_thread.start()

    def update_progress(self, value):
        """Update progress"""
        self.progress_bar.setValue(value)

    def on_validation_finished(self, scanner, error):
        """Validation finished"""
        self.validate_btn.setEnabled(True)
        self.select_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

        if error:
            QMessageBox.critical(self, "Error", f"An error occurred during validation:\n{error}")
            self.stats_label.setText("Validation failed")
            return

        self.scanner = scanner
        self.display_results()

    def display_results(self):
        """Display results"""
        stats = self.scanner.get_statistics()

        # Display valid files
        for file_info in self.scanner.valid_files:
            # Get package type and details
            package_type = file_info.get('package_type', 'Unknown')
            package_details = file_info.get('package_details', {})

            # Set color based on package type
            if package_type == 'NIC包':
                package_color = '#2196F3'  # Blue
            elif package_type == '未知':
                package_color = '#FF9800'  # Orange
            else:
                package_color = '#666666'  # Gray

            # Generate detail information
            detail = ''
            if package_type == 'NIC包':
                time = package_details.get('time', '')
                if time:
                    detail = f'Time: {time}'
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
                'Valid',
                detail,
                '#4CAF50',  # Status color (green)
                package_color  # Package type color
            )

        # Display invalid files
        for file_info in self.scanner.illegal_files:
            self.add_file_row(
                file_info['name'],
                file_info['relative_path'],
                self._format_size(file_info['size']),
                self._get_file_type(file_info['name']),
                '-',
                'Invalid',
                'Invalid file format',
                '#F44336',  # Status color (red)
                '#666666'  # Package type color (gray)
            )

        # Update statistics
        self.stats_label.setText(
            f"Total: {stats['total_files']} files | "
            f"Valid: {stats['valid_files']} | "
            f"Invalid: {stats['illegal_files']}"
        )

        self.statusBar.showMessage(f"Scan completed: {stats['total_files']} files found")
        self.export_btn.setEnabled(True)

        # Show alert
        if stats['illegal_files'] > 0:
            QMessageBox.warning(
                self,
                "Scan Completed",
                f"Scan completed!\n\n"
                f"Total files: {stats['total_files']}\n"
                f"Valid files: {stats['valid_files']}\n"
                f"Invalid files: {stats['illegal_files']}\n\n"
                f"Please check the invalid files in the table."
            )
        else:
            QMessageBox.information(
                self,
                "Scan Completed",
                f"Scan completed!\n\n"
                f"All {stats['total_files']} files have valid format."
            )

    def add_file_row(self, name, path, size, file_type, package_type, status, detail, status_color, package_color):
        """Add file row to table"""
        row = self.table.rowCount()
        self.table.insertRow(row)

        items = [name, path, size, file_type, package_type, status, detail]

        for col, item_text in enumerate(items):
            item = QTableWidgetItem(str(item_text))
            # Status column (column 5) uses status color
            if col == 5:
                item.setForeground(QColor(status_color))
                item.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            # Package type column (column 4) uses package type color
            elif col == 4:
                item.setForeground(QColor(package_color))
                item.setFont(QFont("Arial", 9))
            self.table.setItem(row, col, item)

    def _format_size(self, size):
        """Format file size"""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size/1024:.1f} KB"
        else:
            return f"{size/(1024*1024):.1f} MB"

    def _get_file_type(self, filename):
        """Get file type"""
        if filename.endswith('.zip'):
            return 'ZIP'
        elif filename.endswith('.tar.gz'):
            return 'TAR.GZ'
        elif filename.endswith('.tar'):
            return 'TAR'
        elif filename.endswith('.xlsx'):
            return 'XLSX'
        else:
            return 'Unknown'

    def export_results(self):
        """Export results"""
        if not self.scanner:
            QMessageBox.warning(self, "Warning", "No results to export")
            return

        # Select save file
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Results",
            f"validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text files (*.txt);;CSV files (*.csv);;All files (*.*)"
        )

        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self._export_csv(file_path)
                else:
                    self._export_txt(file_path)

                QMessageBox.information(self, "Success", f"Results exported to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Export failed:\n{str(e)}")

    def _export_txt(self, filename):
        """Export to text file"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("Network Package Validation Results\n")
            f.write("=" * 50 + "\n")
            f.write(f"Validation time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Package directory: {self.current_dir}\n")
            f.write(f"Supported formats: ZIP, TAR.GZ, TAR, XLSX\n")
            f.write("\n")

            # Statistics
            stats = self.scanner.get_statistics()
            if stats:
                f.write(f"Statistics:\n")
                f.write(f"  Total files: {stats['total_files']}\n")
                f.write(f"  Valid files: {stats['valid_files']}\n")
                f.write(f"  Invalid files: {stats['illegal_files']}\n")
                f.write("\n")

            # Detailed results
            f.write("Detailed Results:\n")
            f.write("-" * 50 + "\n")

            for row in range(self.table.rowCount()):
                f.write(f"Filename: {self.table.item(row, 0).text()}\n")
                f.write(f"Path: {self.table.item(row, 1).text()}\n")
                f.write(f"Size: {self.table.item(row, 2).text()}\n")
                f.write(f"Format: {self.table.item(row, 3).text()}\n")
                f.write(f"Package Type: {self.table.item(row, 4).text()}\n")
                f.write(f"Status: {self.table.item(row, 5).text()}\n")
                detail = self.table.item(row, 6).text()
                if detail:
                    f.write(f"Details: {detail}\n")
                f.write("\n")

    def _export_csv(self, filename):
        """Export to CSV file"""
        import csv

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Filename', 'Path', 'Size', 'Format', 'Package Type', 'Status', 'Details'])

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
    window = ValidatorApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
