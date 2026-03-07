import os
import sys
import traceback
from datetime import datetime
import PySimpleGUI as sg
# 添加当前目录到sys.path以支持模块导入
if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.file_scanner import FileScanner

sg.theme('LightGrey')
sg.set_options(font=('Helvetica', 10))

class ValidatorApp:
    def __init__(self):
        self.current_dir = ""
        self.scanner = None
        self.validation_results = []

        # 创建窗口
        self.create_window()

    def create_window(self):
        # 表格列定义
        self.columns = ['文件名', '文件路径', '大小', '格式', '状态', '详情']
        self.tree_data = []

        layout = [
            # 顶部操作区
            [
                sg.Text('请选择数据包目录:', size=(18, 1)),
                sg.InputText(key='-DIR-', size=(60, 1), readonly=True),
                sg.FolderBrowse(target='-DIR-', button_text='选择目录'),
                sg.Button('🔍 开始校验', key='-VALIDATE-', button_color=('white', '#4CAF50')),
            ],

            # 进度条
            [
                sg.Text('进度:'),
                sg.ProgressBar(100, orientation='h', size=(60, 20), key='-PROGRESS-'),
            ],

            # 分隔线
            [sg.HSeparator()],

            # 结果表格
            [
                sg.Table(
                    values=self.tree_data,
                    headings=self.columns,
                    max_col_width=30,
                    auto_size_columns=True,
                    display_row_numbers=False,
                    justification='left',
                    num_rows=15,
                    key='-TABLE-',
                    vertical_scroll_only=False,
                    row_height=30,
                    col_widths=[15, 25, 10, 8, 8, 25],
                    enable_events=True,
                    select_mode=sg.TABLE_SELECT_MODE_BROWSE
                )
            ],

            # 统计信息
            [
                sg.Text('状态:', size=(8, 1)),
                sg.Text('准备就绪', key='-STATUS-', size=(80, 1)),
            ],

            # 底部按钮
            [
                sg.Button('📊 导出结果', key='-EXPORT-', button_color=('white', '#2196F3')),
                sg.Button('退出', key='-EXIT-'),
            ]
        ]

        self.window = sg.Window('网络数据包校验工具', layout, size=(1000, 700), finalize=True)

    def update_table(self):
        """更新表格数据"""
        if self.scanner:
            self.tree_data = []

            # 添加合法文件
            for file_info in self.scanner.valid_files:
                self.tree_data.append([
                    file_info['name'],
                    file_info['relative_path'],
                    self._format_size(file_info['size']),
                    self._get_file_type(file_info['name']),
                    '✅ 合法',
                    ''
                ])

            # 添加非法文件
            for file_info in self.scanner.illegal_files:
                self.tree_data.append([
                    file_info['name'],
                    file_info['relative_path'],
                    self._format_size(file_info['size']),
                    self._get_file_type(file_info['name']),
                    '❌ 非法',
                    '数据包格式非法'
                ])

            self.window['-TABLE-'].update(values=self.tree_data)

    def run(self):
        """主循环"""
        while True:
            event, values = self.window.read()

            if event in (sg.WIN_CLOSED, '-EXIT-'):
                break

            elif event == '-VALIDATE-':
                self.validate_all()

            elif event == '-EXPORT-':
                self.export_results()

        self.window.close()

    def validate_all(self):
        """开始校验"""
        self.current_dir = values['-DIR-']

        if not self.current_dir:
            sg.popup_warning('请先选择数据包目录', title='警告')
            return

        try:
            # 清空结果
            self.tree_data = []
            self.window['-TABLE-'].update(values=[])
            self.window['-PROGRESS-'].update(0)
            self.window['-STATUS-'].update('正在扫描文件...')
            self.window.refresh()

            # 扫描目录
            self.scanner = FileScanner(self.current_dir)
            self.scanner.scan_directory()

            # 获取统计
            stats = self.scanner.get_statistics()
            self.window['-STATUS-'].update(f'扫描完成: 共找到 {stats["total_files"]} 个文件')

            # 更新表格
            self.update_table()

            # 更新进度
            self.window['-PROGRESS-'].update(100)
            self.window.refresh()

            # 显示统计
            sg.popup(f'扫描完成！\n\n总文件数: {stats["total_files"]}\n合法文件: {stats["valid_files"]}\n非法文件: {stats["illegal_files"]}',
                    title='扫描结果')

        except Exception as e:
            sg.popup_error(f'校验过程中发生错误: {str(e)}', title='错误')
            traceback.print_exc()

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
            sg.popup_warning('没有可导出的结果', title='警告')
            return

        # 选择保存文件
        save_path = sg.popup_get_file('保存结果', save_as=True, default_extension='.txt',
                                      file_types=(('文本文件', '*.txt'), ('CSV文件', '*.csv'), ('所有文件', '*.*')))

        if save_path:
            try:
                if save_path.endswith('.csv'):
                    self._export_csv(save_path)
                else:
                    self._export_txt(save_path)

                sg.popup_ok(f'结果已导出到: {save_path}', title='成功')
            except Exception as e:
                sg.popup_error(f'导出失败: {str(e)}', title='错误')

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

            for row in self.tree_data:
                f.write(f"文件名: {row[0]}\n")
                f.write(f"路径: {row[1]}\n")
                f.write(f"大小: {row[2]}\n")
                f.write(f"格式: {row[3]}\n")
                f.write(f"状态: {row[4]}\n")
                if row[5]:
                    f.write(f"详情: {row[5]}\n")
                f.write("\n")

    def _export_csv(self, filename):
        """导出为CSV文件"""
        import csv

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(self.columns)
            writer.writerows(self.tree_data)

if __name__ == "__main__":
    app = ValidatorApp()
    app.run()
