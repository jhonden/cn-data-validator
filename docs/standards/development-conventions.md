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
