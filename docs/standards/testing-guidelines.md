# 测试规范

本文档规定了项目的测试开发规范，确保所有功能的测试用例设计和实现符合统一标准。

## 📋 目录

1. [测试目录组织](#测试目录组织)
2. [测试类型定义](#测试类型定义)
3. [测试用例设计规范](#测试用例设计规范)
4. [测试代码编写规范](#测试代码编写规范)
5. [测试执行规范](#测试执行规范)
6. [测试维护规范](#测试维护规范)
7. [测试覆盖度要求](#测试覆盖度要求)

---

## 测试目录组织

### 目录结构

```
tests/
├── README.md                 # 测试入口文档
├── docs/                    # 测试文档
│   ├── test-coverage-analysis.md      # 测试覆盖度分析
│   ├── test-summary.md               # 测试总结报告
│   └── requirements-mapping.md      # 需求-测试用例映射表
├── unit/                     # 单元测试（按模块）
│   └── test_<module_name>.py
├── integration/              # 集成测试（按功能流程）
│   └── test_<feature_name>.py
├── e2e/                      # 端到端测试（完整用户场景）
│   └── test_<scenario_name>.py
├── data/                     # 测试数据
│   ├── test_data/                     # 通用测试数据
│   └── test_packages/                # 测试包样本
└── shared/                   # 共享测试工具
    ├── README.md
    └── utils/
        └── test_data_generator/        # 测试数据生成器
```

### 放置原则

| 测试类型 | 放置位置 | 说明 |
|---------|----------|------|
| 单个函数/类测试 | `unit/` | 测试独立模块，不依赖外部系统 |
| 多模块协作测试 | `integration/` | 测试模块间接口和数据流 |
| 完整用户场景测试 | `e2e/` | 模拟真实用户操作流程 |
| 测试文档 | `docs/` | 测试相关文档集中管理 |
| 测试数据 | `data/` | 测试用到的数据和样本 |
| 共享测试工具 | `shared/` | 可复用的测试辅助工具 |

---

## 测试类型定义

### 单元测试 (Unit Test)

**定义**：测试最小的可测试单元（函数、方法、类）

**特点**：
- 测试范围小、执行快速（<1秒）
- 不依赖外部系统（文件系统、网络、数据库）
- 使用Mock隔离依赖
- 易于定位问题

**示例**：
```python
def test_is_valid_file():
    """测试文件类型判断逻辑"""
    scanner = FileScanner('/tmp')
    assert scanner._is_valid_file('test.tar.gz') == True
    assert scanner._is_valid_file('test.txt') == False
```

**放置位置**：`tests/unit/`

---

### 集成测试 (Integration Test)

**定义**：测试多个模块协同工作的功能流程

**特点**：
- 测试范围中等（1-10秒）
- 涉及真实模块接口
- 验证系统集成正确性
- 可能依赖文件系统等外部资源

**示例**：
```python
def test_nic_validation_flow():
    """测试NIC包完整验证流程"""
    nic_path = create_test_nic_package()
    validator = NICValidator(nic_path)
    result = validator.validate()
    assert result['valid'] == True
    assert len(result['ne_instances']) > 0
```

**放置位置**：`tests/integration/`

---

### 端到端测试 (End-to-End Test)

**定义**：从用户角度测试完整的业务场景

**特点**：
- 测试范围大、执行较慢（>10秒）
- 模拟真实用户操作
- 验证系统满足业务需求
- 可能涉及GUI/CLI交互

**示例**：
```python
def test_full_validation_workflow():
    """测试完整的验证工作流"""
    # 1. 用户选择目录
    # 2. 系统扫描文件
    # 3. 系统识别包类型
    # 4. 系统执行深度校验
    # 5. 系统展示结果
    # 6. 用户导出结果
    pass  # 实现完整流程测试
```

**放置位置**：`tests/e2e/`

---

## 测试用例设计规范

### 测试用例结构

每个测试用例必须包含以下部分：

```python
def test_<功能描述>():
    """
    [简短描述]

    测试目标：验证<被测功能>在<特定条件下>的行为

    前置条件：<条件描述>
    输入：<输入数据>
    期望输出：<预期结果>
    """
    # 1. 准备测试数据 (Arrange)
    # 2. 执行被测功能 (Act)
    # 3. 断言结果 (Assert)
    # 4. 清理资源 (Clean)
```

### 命名规范

**文件命名**：
- 格式：`test_<模块/功能/场景>.py`
- 示例：`test_file_scanner.py`, `test_nic_validation.py`

**函数命名**：
- 格式：`test_<具体功能>[_<场景>]`
- 示例：`test_is_valid_file`, `test_scan_large_directory`
- 使用下划线分隔单词，小写

**类命名**（如果使用类）：
- 格式：`Test<功能模块>Comprehensive`
- 示例：`TestFileScannerComprehensive`, `TestErrorHandling`

### 测试用例覆盖维度

设计测试用例时，必须覆盖以下维度：

#### 1. 正常场景 (Happy Path)
- 功能在正常输入下的预期行为
- 示例：标准NIC包应该验证通过

#### 2. 边界条件 (Boundary Conditions)
- 输入的边界值
- 示例：24小时时间范围（刚好满足/刚好不满足）

#### 3. 异常场景 (Edge Cases)
- 异常输入和错误情况
- 示例：空文件、损坏文件、不存在文件

#### 4. 性能场景 (Performance)
- 大文件、大量文件处理
- 示例：10MB文件、1000个文件

#### 5. 兼容性场景 (Compatibility)
- 不同系统、不同编码、不同文件格式
- 示例：大小写混合的文件名、中文路径

### 测试用例设计清单

设计测试用例时，回答以下问题：

- [ ] **正常场景**：功能在正常情况下是否工作？
- [ ] **边界条件**：边界值是否正确处理？
- [ ] **异常场景**：错误情况是否正确处理？
- [ ] **性能**：大规模数据是否正常处理？
- [ ] **兼容性**：不同平台/格式是否支持？
- [ ] **可追溯**：需求/缺陷是否可追溯？

---

## 测试代码编写规范

### 文件头规范

每个测试文件必须包含标准文件头：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试<模块/功能名称>

测试范围：<模块/功能>的完整测试
测试目标：验证<核心功能>的正确性、边界条件、异常处理
"""
```

### 导入规范

```python
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# 从项目根目录导入模块
from src.service.file_scanner import FileScanner
from src.service.nic_validator import NICValidator
```

**注意**：
- 不要从 `utils/`, `service/`, `view/` 导入（旧路径）
- 必须从 `src.service/`, `src.view/` 导入（新路径）
- 路径计算要适应文件所在目录（unit/integration/e2e）

### 路径计算规范

不同测试层级的路径计算：

```python
# 单元测试（tests/unit/）
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 集成测试（tests/integration/）
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# E2E测试（tests/e2e/）
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

### 断言规范

**使用assert进行断言**，不要使用print判断：

```python
# ✅ 正确
assert result['valid'] == True, "Expected valid=True"

# ❌ 错误
if result['valid'] == True:
    print("Pass")
```

**断言失败时提供清晰错误信息**：

```python
# ✅ 正确
assert len(ne_instances) == 2, f"Expected 2 NE instances, got {len(ne_instances)}"

# ❌ 错误
assert len(ne_instances) == 2
```

### 测试隔离规范

每个测试必须独立运行，不依赖其他测试：

```python
class TestFileScannerComprehensive:
    def setup_method(self):
        """每个测试方法前的设置"""
        self.test_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """每个测试方法后的清理"""
        if self.test_dir:
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_something(self):
        # 使用 self.test_dir
        pass
```

### 临时文件规范

**必须清理临时文件**：

```python
def test_something():
    temp_dir = tempfile.mkdtemp(prefix='test_')
    try:
        # 测试代码
        pass
    finally:
        # 清理
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
```

**临时目录命名规范**：
- 单元测试：`tempfile.mkdtemp()` 使用默认前缀
- 集成测试：使用有意义的前缀，如 `nic_test_`, `scan_test_`

### 测试输出规范

**使用emoji标记测试状态**：

```python
print("\n🔍 测试1: 复杂目录结构扫描")  # 开始测试
print("✅ 扫描完成，发现8个文件")      # 测试通过
print("❌ 测试失败: <错误信息>")         # 测试失败
print("⚠️  测试出现警告: <警告信息>")     # 测试警告
```

**测试结果汇总**：

```python
print("\n" + "=" * 70)
print(f" 综合测试结果: {passed_tests}/{total_tests} 通过")
print("=" * 70)

if passed_tests == total_tests:
    print("🎉 所有综合测试通过！")
    return True
```

### Mock使用规范

**Mock用于隔离外部依赖**：

```python
import unittest.mock as mock

def test_with_mock():
    """使用Mock测试"""
    # Mock外部依赖
    with mock.patch('src.service.nic_validator.StaticMMLChecker') as mock_checker:
        mock_checker.return_value.check_package.return_value = {...}

        # 执行测试
        validator = NICValidator('test.tar.gz')
        result = validator.validate()

        # 断言Mock被调用
        mock_checker.return_value.check_package.assert_called_once()
```

---

## 测试执行规范

### 运行单个测试

```bash
# 单元测试
python3 tests/unit/test_file_scanner.py

# 集成测试
python3 tests/integration/test_nic_validation.py

# E2E测试
python3 tests/e2e/test_full_workflow.py
```

### 运行所有测试

```bash
# 单元测试
python3 tests/unit/test_*.py

# 集成测试
python3 tests/integration/test_*.py

# 所有测试
python3 tests/unit/test_*.py && \
python3 tests/integration/test_*.py && \
python3 tests/e2e/test_*.py
```

### 测试结果验证

**必须满足以下标准才能提交**：

- [ ] 所有测试用例通过
- [ ] 无警告信息（除了预期的）
- [ ] 测试覆盖度达到要求
- [ ] 测试文档已更新

### CI/CD集成

**自动化测试流程**：

```bash
# 1. 编译检查
python3 -m py_compile tests/**/*.py

# 2. 运行测试
python3 tests/unit/test_*.py
python3 tests/integration/test_*.py

# 3. 生成测试报告
python3 tests/generate_coverage_report.py
```

---

## 测试维护规范

### 文件维护

**保持测试文件与源码同步**：
- 源码重构时，同步更新测试
- 新增功能时，立即编写测试
- 删除功能时，移除对应测试

### 文档维护

**每次测试变更后更新文档**：

1. **更新 requirements-mapping.md**
   - 新需求：添加需求和测试用例映射
   - 需求变更：更新测试用例对应关系
   - 需求废弃：标记为已废弃

2. **更新 test-summary.md**
   - 新增测试用例：更新测试结果统计
   - 修复Bug：记录问题修复验证
   - 性能优化：记录性能测试结果

3. **更新 test-coverage-analysis.md**
   - 定期分析测试覆盖度
   - 识别测试盲区
   - 提出改进建议

### 测试数据维护

**定期更新测试数据**：
- 新增NE类型：更新配置文件
- 规则变更：更新测试期望
- 样本更新：替换过期测试数据

### 版本管理

**测试与功能版本同步**：
- 测试代码与功能代码同一commit提交
- 新功能包含测试（TDD流程）
- Bug修复包含回归测试

---

## 测试覆盖度要求

### 覆盖度目标

| 测试类型 | 目标覆盖度 | 说明 |
|---------|-----------|------|
| 单元测试 | 90%+ | 核心业务逻辑 |
| 集成测试 | 80%+ | 主要功能流程 |
| E2E测试 | 60%+ | 关键用户场景 |

### 覆盖度测量

**使用工具进行精确测量**（计划中）：

```bash
# 安装pytest和覆盖率工具
pip install pytest pytest-cov

# 运行测试并生成覆盖率报告
pytest tests/ --cov=src --cov-report=html

# 查看报告
open htmlcov/index.html
```

### 覆盖度指标

**关键指标**：
- **行覆盖率** (Line Coverage)：执行的代码行比例
- **分支覆盖率** (Branch Coverage)：条件分支的覆盖比例
- **函数覆盖率** (Function Coverage)：被调用的函数比例

### 覆盖度审查

**定期（每月）进行覆盖度审查**：

1. 生成覆盖率报告
2. 识别未覆盖的代码
3. 分析未覆盖原因：
   - 遗忘代码 → 补充测试
   - 废弃代码 → 清理代码
   - 难以测试 → 设计Mock方案

---

## 开发流程

### 功能开发测试流程

**标准流程**（TDD推荐）：

```
1. 需求分析
   └─> 理解需求，明确验收标准

2. 测试设计
   └─> 设计测试用例（正常、边界、异常）
   └─> 更新 requirements-mapping.md

3. 测试实现（先）
   └─> 编写测试代码（运行失败）

4. 功能实现（后）
   └─> 编写功能代码（测试通过）

5. 测试验证
   └─> 运行所有测试
   └─> 确保无回归

6. 代码提交
   └─> 功能代码 + 测试代码 + 文档更新
```

### Bug修复测试流程

```
1. Bug定位
   └─> 定位问题代码

2. 复现测试
   └─> 编写测试复现Bug

3. 修复验证
   └─> 修复代码
   └─> 测试通过

4. 回归测试
   └─> 运行相关测试
   └─> 确保无新问题

5. 提交修复
   └─> Bug修复 + 复现测试 + 回归验证
```

---

## 最佳实践

### 1. 测试先行（TDD）
- 先写测试，再写功能
- 让测试驱动设计

### 2. 测试独立性
- 每个测试独立运行
- 不依赖测试执行顺序

### 3. 测试可读性
- 测试即文档
- 使用清晰的命名和注释

### 4. 测试快速
- 单元测试<1秒
- 集成测试<10秒
- 避免不必要的等待

### 5. 测试自动化
- 可一键运行所有测试
- CI/CD自动执行

### 6. 测试真实性
- 使用真实数据结构
- 模拟真实使用场景

---

## 附录

### A. 测试用例设计示例

**功能：文件扫描器 - 文件类型检测**

| 场景 | 输入 | 期望输出 | 测试类型 |
|------|------|----------|---------|
| 标准tar.gz | test.tar.gz | True | 正常 |
| 大写扩展名 | test.TAR.GZ | True | 兼容性 |
| 不支持格式 | test.txt | False | 异常 |
| 特殊文件名 | test..tar.gz | True | 边界 |

### B. 测试代码检查清单

提交前检查：

- [ ] 所有测试通过
- [ ] 无语法错误（python -m py_compile）
- [ ] 导入路径正确
- [ ] 无硬编码路径
- [ ] 临时文件已清理
- [ ] 断言信息清晰
- [ ] 测试覆盖需求文档

### C. 常见问题

**Q1: Mock和真实的测试如何选择？**
- 单元测试：用Mock隔离依赖
- 集成测试：用真实依赖验证集成

**Q2: 测试覆盖率100%是目标吗？**
- 不是，追求有意义覆盖
- 重点是核心逻辑和关键路径

**Q3: GUI测试如何做？**
- 业务逻辑测试为主
- GUI交互测试使用E2E

---

**文档版本**: 1.0
**最后更新**: 2026-03-10
**维护者**: 项目团队
