# 编码规范

本文档定义了网络数据包校验工具项目（Python + PyQt6 桌面应用）的编码规范。

**来源**：参考 operator-manager 项目的开发规范，适配 Python 桌面应用场景

---

## 1. 文档和注释语言规范

**重要：因为项目在中国开发，以下情况必须优先使用中文：**

### 1.1 代码注释

- 业务逻辑注释必须使用中文
- 复杂算法或配置说明必须使用中文
- 示例：
  ```python
  # 检查 NIC 包是否包含必需的时间文件夹和报告文件
  if not self._validate_nic_package_structure(file_path):
      raise ValidationError("NIC 包结构不符合要求，必须包含时间文件夹和报告文件")
  ```

### 1.2 文档输出

- 代码文档（docstring）优先使用中文
- 架构设计文档、README 使用中文
- 用户手册、开发指南使用中文

### 1.3 日志输出

- 应用日志信息使用英文
- 错误提示信息使用中文
- 示例：`logger.error("package validation failed: {}", package_name)`

### 1.4 用户界面文本

- GUI 界面文本使用中文
- 错误提示、警告信息使用中文
- 示例：QMessageBox.warning("警告", "请先选择数据包目录")

### 1.5 例外情况

- 技术术语保持英文（如 PyQt6、tarfile、json、zipfile 等）
- 变量名、类名、方法名等标识符使用英文
- 配置文件中的 key 使用英文
- 代码的运行日志输出使用英文（便于日志分析和问题排查）

---

## 2. Python 开发规范

### 2.1 编码规范

- 遵循 PEP 8 编码规范
- 使用蛇形命名法（snake_case）命名变量和方法
- 使用大驼峰命名法（PascalCase）命名类
- 常量使用全大写下划线分隔（UPPER_SNAKE_CASE）

### 2.2 文件格式规范

#### 2.2.1 换行符规范（必须遵循）

**⚠️ 关键规则：Windows批处理文件必须使用CRLF换行符**

由于本项目在Mac/Linux环境开发，但最终在Windows环境执行，必须严格遵守以下换行符规则：

| 文件类型 | 必须使用换行符 | 说明 |
|---------|---------------|------|
| `.bat`、`.cmd` | **CRLF (`\r\n`)** | Windows批处理文件必须使用CRLF，否则无法正常执行 |
| Python文件 (`.py`) | LF (`\n`) | Python文件使用标准Unix换行符（开发环境默认） |
| Shell脚本 (`.sh`) | LF (`\n`) | Shell脚本使用Unix换行符 |
| Markdown文件 (`.md`) | LF (`\n`) | 文档文件使用Unix换行符 |
| 其他配置文件 | LF (`\n`) | 默认使用Unix换行符 |

#### 2.2.2 批处理文件处理要求

**创建/修改 `.bat` 文件时必须：**

1. **使用CRLF换行符**
   - Mac/Linux: 使用 `unix2dos` 工具转换
   ```bash
   unix2dos build_windows.bat
   ```
   - 或使用 `sed` 命令：
   ```bash
   sed -i '' 's/$/\r/' build_windows.bat
   ```

2. **验证换行符**
   ```bash
   # 查看字节格式，应显示 \r\n
   od -c build_windows.bat | head -10
   ```

3. **提交前检查**
   - 所有 `.bat` 和 `.cmd` 文件必须验证使用CRLF
   - Git提交前必须确认文件换行符正确

#### 2.2.3 Windows执行环境编码

**Windows批处理脚本必须设置UTF-8编码环境变量：**

```batch
@echo off
REM 设置Python编码为UTF-8
set PYTHONIOENCODING=utf-8
chcp 65001 >nul
```

这样可以确保：
- Python脚本正确识别UTF-8编码
- 中文输出在Windows命令行中正常显示
- 避免编码相关错误

#### 2.2.4 Python文件编码声明

**所有Python文件必须添加UTF-8编码声明（文件第一行或第二行）：**

```python
# -*- coding: utf-8 -*-
```

对于有shebang行的文件：
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
```

#### 2.2.5 编码问题排查清单

如果在Windows上遇到编码或执行问题，按以下顺序检查：

- [ ] `.bat` 文件是否使用CRLF换行符
- [ ] `.bat` 文件是否设置 `PYTHONIOENCODING=utf-8`
- [ ] Python文件是否包含 `# -*- coding: utf-8 -*-` 声明
- [ ] 是否在cmd中执行了 `chcp 65001`（或在bat中已设置）
- [ ] Windows系统是否启用了"UTF-8提供全球语言支持"（可选但推荐）

### 2.2 异常处理

- 使用自定义异常类
- 异常消息使用中文
- 不要捕获异常后直接忽略，至少记录日志
- 示例：
  ```python
  try:
      scanner.scan_directory()
  except Exception as e:
      logger.error(f"扫描目录失败: {str(e)}")
      raise ScanError(f"扫描目录失败: {str(e)}")
  ```

### 2.3 日志规范

- 使用 Python logging 模块
- 日志级别使用：
  - `ERROR`: 错误信息
  - `WARNING`: 警告信息
  - `INFO`: 关键业务流程
  - `DEBUG`: 调试信息（仅开发环境）
- 日志格式：使用中文描述，占位符输出关键参数

### 2.4 文件操作规范

- 使用 `with` 语句处理文件操作，确保资源正确释放
- 示例：
  ```python
  with open(filename, 'r', encoding='utf-8') as f:
      content = f.read()
  ```

---

## 3. PyQt6 GUI 开发规范

### 3.1 代码组织

- 使用多线程处理耗时操作，避免阻塞 UI
- 主线程只负责 UI 更新，业务逻辑在工作线程中执行
- 示例：
  ```python
  class ValidationThread(QThread):
      finished = pyqtSignal(object, str)

      def run(self):
          # 耗时操作在工作线程执行
          scanner = FileScanner(self.directory)
          scanner.scan_directory()
          self.finished.emit(scanner, "")
  ```

### 3.2 资源管理

- 及时释放文件资源，使用临时目录后必须清理
- 使用 `tempfile.TemporaryDirectory()` 自动管理临时目录

### 3.3 界面响应

- 耗时操作期间禁用相关按钮
- 显示进度条或加载状态
- 操作完成后恢复按钮状态

---

## 4. 测试规范

### 4.1 单元测试

- 核心业务逻辑必须有单元测试
- 测试覆盖率不低于 70%
- 测试类命名：`{类名}Test`
- 测试文件位于 `tests/` 目录

### 4.2 集成测试

- 关键功能必须有集成测试
- 使用测试脚本进行功能测试

---

## 5. 安全规范

### 5.1 输入验证

- 所有用户输入必须进行验证
- 目录路径必须验证其存在性和有效性
- 文件格式必须验证支持的扩展名

### 5.2 文件操作安全

- 解压文件前验证文件大小，避免解压炸弹
- 限制解压深度和文件数量
- 示例：
  ```python
  # 验证文件大小
  if os.path.getsize(file_path) > MAX_FILE_SIZE:
      raise FileSizeError("文件过大，请检查文件来源")
  ```

---

## 6. Git 工作流规范

- 每个功能开发一个分支
- 功能完成后合并到 main 分支
- 合并前确保功能验证通过
- 详细流程见：[代码提交流程](./code-submission-workflow.md)

---

**相关文档**:
- [代码提交流程](./code-submission-workflow.md) - 代码验证和提交
- [项目约束](./project-constraints.md) - 项目关键约束

---

**文档维护者**: Claude AI Assistant
**最后更新**: 2026-03-06
