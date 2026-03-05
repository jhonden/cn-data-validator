import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import os
import sys
import traceback
from datetime import datetime
from utils.file_scanner import FileScanner

# 设置 customtkinter 主题
ctk.set_appearance_mode("System")  # 可以选择 "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # 可以选择 "blue", "green", "dark-blue"

class ValidatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("网络数据包校验工具")
        self.root.geometry("1000x700")

        self.current_dir = ""
        self.scanner = None
        self.validation_results = []

        # 设置界面样式
        self.setup_ui()

    def setup_ui(self):
        """设置界面"""
        # 顶部操作区
        control_frame = tk.Frame(self.root, pady=10, bg='#f0f0f0')
        control_frame.pack(fill=tk.X, padx=10)

        # 左侧：目录选择
        left_frame = tk.Frame(control_frame, bg='#f0f0f0')
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.dir_btn = ctk.CTkButton(left_frame, text="📁 选择数据包目录",
                                    command=self.select_directory, width=180)
        self.dir_btn.pack(side=tk.LEFT, padx=5)

        self.dir_label = ctk.CTkLabel(left_frame, text="请选择数据包目录",
                                    font=('Arial', 10))
        self.dir_label.pack(side=tk.LEFT, padx=10)

        # 右侧：开始校验
        self.validate_btn = ctk.CTkButton(control_frame, text="🔍 开始校验",
                                        command=self.validate_all, width=150,
                                        fg_color="#4CAF50", hover_color="#45a049")
        self.validate_btn.pack(side=tk.RIGHT, padx=5)

        # 进度条
        self.progress = ctk.CTkProgressBar(control_frame, width=300)
        self.progress.pack(side=tk.RIGHT, padx=10)
        self.progress.set(0)

        # 结果区域
        result_frame = tk.Frame(self.root)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 表格
        columns = ('文件名', '文件路径', '大小', '格式', '状态', '详情')
        self.tree = ttk.Treeview(result_frame, columns=columns, show='headings', height=12)

        # 设置列
        column_widths = {
            '文件名': 180,
            '文件路径': 250,
            '大小': 80,
            '格式': 100,
            '状态': 100,
            '详情': 200
        }

        for col, width in column_widths.items():
            self.tree.heading(col, text=col, anchor=tk.CENTER)
            self.tree.column(col, width=width, anchor=tk.CENTER)

        # 配置列
        self.tree.column('文件路径', stretch=True)
        self.tree.column('详情', stretch=True)

        # 滚动条
        v_scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(result_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # 布局
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')

        result_frame.grid_rowconfigure(0, weight=1)
        result_frame.grid_columnconfigure(0, weight=1)

        # 导出按钮
        export_frame = tk.Frame(self.root, bg='#f0f0f0')
        export_frame.pack(fill=tk.X, padx=10, pady=5)

        self.export_btn = ctk.CTkButton(export_frame, text="📊 导出结果",
                                      command=self.export_results,
                                      width=150, fg_color="#2196F3")
        self.export_btn.pack(side=tk.RIGHT, padx=5)

        # 底部状态栏
        self.status_label = ctk.CTkLabel(self.root, text="准备就绪",
                                       anchor=tk.W,
                                       font=('Arial', 9))
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)

    def select_directory(self):
        """选择目录"""
        directory = filedialog.askdirectory(title="选择数据包目录")
        if directory:
            self.current_dir = directory
            self.dir_label.config(text=f"当前目录: {os.path.basename(directory)}")
            self.status_label.config(text=f"已选择目录: {directory}")

    def validate_all(self):
        """开始校验"""
        if not self.current_dir:
            messagebox.showwarning("警告", "请先选择数据包目录")
            return

        # 清空结果
        self.tree.delete(*self.tree.get_children())
        self.validation_results = []
        self.progress['value'] = 0

        # 禁用按钮
        self.dir_btn.config(state=tk.DISABLED)
        self.validate_btn.config(state=tk.DISABLED)
        self.root.update()

        try:
            # 扫描目录
            self.status_label.config(text="正在扫描文件...")
            self.scanner = FileScanner(self.current_dir)
            self.scanner.scan_directory()

            # 获取统计
            stats = self.scanner.get_statistics()
            self.status_label.config(text=f"扫描完成: 共找到 {stats['total_files']} 个文件")

            # 显示结果
            self.display_results()

            # 更新进度
            self.progress['value'] = 100

        except Exception as e:
            messagebox.showerror("错误", f"校验过程中发生错误: {str(e)}")
            traceback.print_exc()

        finally:
            # 启用按钮
            self.dir_btn.config(state=tk.NORMAL)
            self.validate_btn.config(state=tk.NORMAL)
            self.root.update()

    def display_results(self):
        """显示结果"""
        # 显示合法文件
        for file_info in self.scanner.valid_files:
            self.tree.insert('', 'end', values=(
                file_info['name'],
                file_info['relative_path'],
                self._format_size(file_info['size']),
                self._get_file_type(file_info['name']),
                '✅ 合法',
                ''
            ))

        # 显示非法文件
        for file_info in self.scanner.illegal_files:
            self.tree.insert('', 'end', values=(
                file_info['name'],
                file_info['relative_path'],
                self._format_size(file_info['size']),
                self._get_file_type(file_info['name']),
                '❌ 非法',
                '数据包格式非法'
            ))

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
            messagebox.showwarning("警告", "没有可导出的结果")
            return

        # 选择保存文件
        export_file = filedialog.asksaveasfilename(
            title="保存结果",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )

        if export_file:
            try:
                if export_file.endswith('.csv'):
                    self._export_csv(export_file)
                else:
                    self._export_txt(export_file)

                messagebox.showinfo("成功", f"结果已导出到: {export_file}")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {str(e)}")

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

            # 详细结果
            f.write("详细结果:\n")
            f.write("-" * 50 + "\n")

            for item in self.tree.get_children():
                values = self.tree.item(item)['values']
                f.write(f"文件名: {values[0]}\n")
                f.write(f"路径: {values[1]}\n")
                f.write(f"大小: {values[2]}\n")
                f.write(f"格式: {values[3]}\n")
                f.write(f"状态: {values[4]}\n")
                if values[5]:
                    f.write(f"详情: {values[5]}\n")
                f.write("\n")

    def _export_csv(self, filename):
        """导出为CSV文件"""
        import csv

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['文件名', '文件路径', '大小', '格式', '状态', '详情'])

            for item in self.tree.get_children():
                values = self.tree.item(item)['values']
                writer.writerow(values)

if __name__ == "__main__":
    root = ctk.CTk()
    app = ValidatorApp(root)
    root.mainloop()
