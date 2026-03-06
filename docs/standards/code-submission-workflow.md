# 代码提交流程

**重要规则：修改代码后不要自动提交**

---

## 1. 验证要求

### 1.1 路径检查规则

**⚠️ 重要：执行路径相关命令前必须检查当前工作目录**

在执行编译、打包、启动等与路径强相关的命令前，**必须先检查当前路径是否正确**，避免在错误目录下执行命令。

#### 项目根目录表示

本规约使用 `$PROJECT_ROOT` 表示项目根目录。此变量的值为动态获取：

**获取方式（按优先级）：**

1. **环境变量**（最高优先级）
   ```bash
   # 在 ~/.zshrc 或 ~/.bash_profile 中设置
   export VALIDATOR_HOME=/path/to/cn-data-validator
   ```

2. **Git 仓库根目录检测**（默认方式）
   ```bash
   # 自动检测 Git 仓库根目录
   git rev-parse --show-toplevel
   ```

3. **CLAUDE.md 文件检测**（备用方式）
   ```bash
   # 查找包含 CLAUDE.md 的目录
   find . -maxdepth 3 -name "CLAUDE.md" -type f | head -1
   ```

#### AI 助手行为要求

在会话开始时，AI 助手必须：
1. 读取规范文档
2. **动态获取并记住** `$PROJECT_ROOT` 的实际值
3. **在后续所有命令中优先使用** `$PROJECT_ROOT` 而非硬编码路径
4. 在执行路径相关命令前，检查当前目录是否为 `$PROJECT_ROOT`

#### 正确做法

```bash
# ✅ 使用 $PROJECT_ROOT 变量
cd $PROJECT_ROOT
python3 validator_qt.py

# 或者在命令前检查
if [ "$PWD" != "$PROJECT_ROOT" ]; then
    echo "错误：当前目录不是项目根目录"
    echo "请切换到项目根目录：$PROJECT_ROOT"
    return 1
fi
```

#### 错误做法

```bash
# ❌ 硬编码路径
cd /Users/gaowen/Code/cn-data-validator
python3 validator_qt.py

# ❌ 不检查路径直接执行
python3 validator_qt.py  # 可能不在项目根目录
```

#### 需要检查路径的命令

- 启动程序：`python3 validator_qt.py`、`python3 validator_cli.py`
- 运行测试：`python3 -m pytest tests/`
- 打包应用：`pyinstaller --onefile ...`

---

### 1.2 修改完成后必须验证

- 确保所有模块能够编译通过
- 确保程序能够正常启动
- 验证基本功能正常

---

### 1.3 验证步骤

#### 编译验证

**方式 1：Python 语法检查**
```bash
cd $PROJECT_ROOT
python3 -m py_compile validator_qt.py
python3 -m py_compile validator_cli.py
python3 -m py_compile utils/package_identifier.py
python3 -m py_compile utils/file_scanner.py
```

**方式 2：导入测试**
```bash
cd $PROJECT_ROOT
python3 -c "from validator_qt import ValidatorApp; print('导入成功')"
```

#### 功能验证

- 运行程序：`python3 validator_qt.py`
- 选择测试目录进行校验
- 验证 NIC 包识别功能
- 验证表格显示正常
- 验证导出功能

---

### 1.4 验证通过标准

**验证通过标准：**
- ✅ Python 编译成功（无语法错误）
- ✅ 程序启动成功（无异常）
- ✅ GUI 界面正常显示
- ✅ 功能操作无错误

---

## 2. 提交流程

### 2.1 禁止行为

❌ **严格禁止：**
- 修改代码后立即提交（未验证）
- 存在编译错误时提交
- 存在运行时错误时提交
- 未进行功能验证时提交

---

### 2.2 正确提交流程

**步骤 1：验证完成**
- 确保编译通过
- 确保程序正常启动
- 确保功能验证通过

**步骤 2：询问用户确认**
- 向用户报告验证结果
- 询问用户："代码已验证通过，是否提交？"
- 等待用户明确确认

**步骤 3：执行提交**
```bash
# 只有在用户确认后才执行
cd $PROJECT_ROOT
git add .
git commit -m "类型：简短描述"
git push
```

---

### 2.3 提交信息规范

必须使用中文编写提交信息，格式：
```bash
git commit -m "类型：简短描述"
```

**类型：**
- `feat` - 新功能实现
- `fix` - Bug 修复
- `refactor` - 代码重构
- `docs` - 文档更新
- `test` - 测试相关
- `perf` - 性能优化
- `style` - 代码格式调整

**示例：**
```bash
git commit -m "feat: 添加 NIC 包识别功能"
git commit -m "fix: 修复中文编码问题"
git commit -m "docs: 更新开发规范文档"
```

---

## 3. 常见问题

### Q1: 为什么要这么严格？

**A:** 确保代码质量，避免：
- 提交无法运行的代码
- 提交有明显 Bug 的代码
- 频繁回滚修复
- 破坏项目稳定性

### Q2: 如果验证失败怎么办？

**A:**
1. 分析错误信息
2. 修复问题
3. 重新验证
4. 验证通过后才能考虑提交

### Q3: 调试代码怎么办？

**A:** 调试代码可以提交，但必须：
- 标记为"调试：添加 XXX 日志"
- 确保不影响现有功能
- 尽快移除调试代码
- 移除前再次验证

---

## 4. 检查清单

提交前必须通过以下检查：

1. - [ ] Python 编译成功（python3 -m py_compile）
2. - [ ] 程序正常启动
3. - [ ] 基本功能验证通过
4. - [ ] 用户确认可以提交
5. - [ ] Git 提交信息符合规范
6. - [ ] 已删除不必要的调试代码（如果有的话）

---

**相关文档**:
- [编码规范](./development-conventions.md) - 编码规范
- [项目约束](./project-constraints.md) - 项目关键约束

---

**文档维护者**: Claude AI Assistant
**最后更新**: 2026-03-06
