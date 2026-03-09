# -*- coding: utf-8 -*-
"""
排版令牌系统
Typography Tokens System

定义应用中使用的字体大小、粗细和字体家族。
所有排版设置应从此文件导入，以保持视觉一致性。
"""

# ======== 字体家族 (Font Families) ========

FONTS = {
    'default': 'Arial',           # 默认字体
    'heading': 'Arial',          # 标题字体
    'body': 'Arial',              # 正文字体
    'code': 'Courier New',         # 代码/等宽字体
}

# ======== 字体大小 (Font Sizes) ========

FONT_SIZE = {
    'heading': 16,               # 主标题（16px）
    'section_header': 14,        # 章节标题（14px）
    'body': 12,                  # 正文文本（12-13px）
    'small': 10,                  # 小文本/标签（10-11px）
    'tiny': 9,                    # 极小文本（9px）
}

# ======== 字体粗细 (Font Weights) ========

FONT_WEIGHT = {
    'bold': 'Bold',               # 粗体（用于标题）
    'semibold': 'Bold',           # 半粗体
    'normal': 'Normal',            # 正常（用于正文）
    'light': 'Normal',             # 细体
}

# ======== 辅助函数 (Helper Functions) ========

def get_heading_font():
    """获取标题字体"""
    return {
        'family': FONTS['heading'],
        'size': FONT_SIZE['heading'],
        'weight': FONT_WEIGHT['bold']
    }

def get_section_header_font():
    """获取章节标题字体"""
    return {
        'family': FONTS['section_header'],
        'size': FONT_SIZE['section_header'],
        'weight': FONT_WEIGHT['bold']
    }

def get_body_font():
    """获取正文字体"""
    return {
        'family': FONTS['body'],
        'size': FONT_SIZE['body'],
        'weight': FONT_WEIGHT['normal']
    }

def get_small_font():
    """获取小字体"""
    return {
        'family': FONTS['body'],
        'size': FONT_SIZE['small'],
        'weight': FONT_WEIGHT['normal']
    }

def get_tiny_font():
    """获取极小字体"""
    return {
        'family': FONTS['body'],
        'size': FONT_SIZE['tiny'],
        'weight': FONT_WEIGHT['normal']
    }
