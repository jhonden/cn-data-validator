"""
设计令牌系统
Design Tokens System

定义应用中使用的颜色、间距和排版常量。
所有硬编码值应从此文件导入，以保持设计一致性。
"""

# ======== 颜色令牌 (Color Tokens) ========

COLORS = {
    # 语义化颜色 (Semantic Colors)
    'primary': '#2196F3',           # 主要按钮/操作
    'success': '#4CAF50',           # 成功/有效状态
    'error': '#F44336',             # 错误/无效状态
    'warning': '#FF9800',           # 警告/注意状态
    'info': '#E3F2FD',             # 信息/次要颜色

    # 表面颜色 (Surface Colors)
    'surface': '#ffffff',             # 主背景（白色）
    'surface_alt': '#f5f5f5',       # 次要背景（浅灰）
    'surface_hover': '#E3F2FD',    # 悬停背景（浅蓝）
    'surface_selected': '#BBDEFB',   # 选中背景（中蓝）

    # 边框颜色 (Border Colors)
    'border': '#e0e0e0',            # 浅灰边框
    'border_hover': '#E3F2FD',      # 悬停边框（浅蓝）
    'border_selected': '#BBDEFB',    # 选中边框（中蓝）

    # 文本颜色 (Text Colors)
    'text_primary': '#212121',        # 主要文本（深灰）
    'text_secondary': '#666666',      # 次要文本（中灰）
    'text_hint': '#999999',          # 提示文本（浅灰）
    'text_on_surface': '#212121',    # 白色背景上的文本
    'text_inverse': '#ffffff',        # 彩色背景上的文本（白色）

    # 特殊用途颜色 (Special Purpose Colors)
    'link': '#2196F3',              # 链接文本（蓝色）
    'link_hover': '#1976D2',        # 链接悬停（深蓝）
    'divider': '#e0e0e0',            # 分隔线
}

# ======== 间距令牌 (Spacing Tokens) ========

SPACING = {
    # 基础间距 (Base Spacing)
    'none': 0,
    'tiny': 4,                       # 极小间距（4px）
    'small': 8,                      # 小间距（8px）
    'medium': 12,                     # 中等间距（12px）
    'large': 16,                      # 大间距（16px）
    'xlarge': 20,                    # 超大间距（20px）
    'xxlarge': 24,                   # 特大间距（24px）
}

# ======== 尺寸令牌 (Size Tokens) ========

SIZES = {
    # 按钮尺寸 (Button Sizes)
    'button_small': 100,               # 小按钮（100px）
    'button_medium': 120,              # 中等按钮（120px）
    'button_large': 140,               # 大按钮（140px）

    # 输入框尺寸 (Input Sizes)
    'input_small': 120,               # 小输入框（120px）
    'input_medium': 150,              # 中等输入框（150px）

    # 表格尺寸 (Table Sizes)
    'column_filename': None,            # Filename 列（自动）
    'column_path': None,                # Path 列（Stretch 模式）
    'column_size': None,               # Size 列（自动）
    'column_format': None,              # Format 列（自动）
    'column_type': None,               # Type 列（自动）
    'column_status': None,              # Status 列（自动）
    'column_details': 300,             # Details 列（300px 最小宽度）

    # 进度条尺寸 (Progress Bar Sizes)
    'progress_bar_width': 200,          # 进度条宽度（200px）
    'progress_bar_height': 24,          # 进度条高度（24px）

    # 对话框尺寸 (Dialog Sizes)
    'dialog_width': 950,               # 对话框宽度（950px）
    'dialog_height': 700,              # 对话框高度（700px）
    'dialog_margins': 20,              # 对话框边距（20px）

    # 窗口尺寸 (Window Sizes)
    'window_width': 1200,              # 窗口宽度（1200px）
    'window_height': 700,               # 窗口高度（700px）
}

# ======== 边框半径令牌 (Border Radius Tokens) ========

BORDER_RADIUS = {
    'tiny': 3,                          # 极小圆角（3px）
    'small': 4,                         # 小圆角（4px）
    'medium': 6,                       # 中等圆角（6px）
    'large': 8,                        # 大圆角（8px）
}

# ======== 边框宽度令牌 (Border Width Tokens) ========

BORDER_WIDTH = {
    'none': 0,
    'thin': 1,
    'normal': 2,
    'thick': 3,
}
