#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动脚本 - 从项目根目录运行
"""

import sys
import os

# 确保在项目根目录运行
project_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_root)
sys.path.insert(0, project_root)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        from src.view.validator_cli import ValidatorCLI
        cli = ValidatorCLI()
        cli.run()
    else:
        from src.view.validator_qt import ValidatorApp
        import sys
        app = QApplication(sys.argv)
        validator = ValidatorApp()
        validator.show()
        sys.exit(app.exec())