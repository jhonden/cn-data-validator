# 测试目录

本目录包含项目的所有测试代码、测试文档和测试数据。

## 📁 目录结构

```
tests/
├── README.md                    # 本文档
├── docs/                       # 测试文档
│   ├── test-coverage-analysis.md    # 测试覆盖度分析
│   ├── test-summary.md              # 测试总结报告
│   └── requirements-mapping.md     # 需求-测试用例映射表
├── unit/                       # 单元测试（按模块）
│   ├── test_simple.py                # 基础导入测试
│   ├── test_modules.py              # 模块测试
│   └── test_package_id.py          # 包识别测试
├── integration/                # 集成测试（按功能流程）
│   ├── test_refactored_structure.py # 重构结构测试
│   ├── test_nic_validation.py       # NIC包验证测试
│   ├── test_scenario_validation.py   # 场景验证测试
│   └── test_comprehensive.py       # 综合测试套件
├── e2e/                       # 端到端测试（完整用户场景）
├── data/                      # 测试数据
│   ├── README.md                   # 测试数据说明
│   ├── test_data/                  # 测试数据
│   └── test_packages/             # 测试包
└── shared/                    # 共享测试工具
    ├── utils/
    │   └── test_data_generator/     # 测试数据生成器
    └── README.md
```

## 🎯 测试类型说明

### 单元测试 (unit/)
测试单个函数、类或模块的功能，确保基本逻辑正确。

**特点**：
- 测试范围小、执行快
- 不依赖外部系统
- 容易定位问题

**示例**：
- `test_simple.py` - 测试模块导入
- `test_package_id.py` - 测试包识别逻辑

### 集成测试 (integration/)
测试多个模块协同工作的功能流程，验证模块间的接口和数据流。

**特点**：
- 测试范围中等
- 涉及多个模块协作
- 验证系统集成正确性

**示例**：
- `test_nic_validation.py` - 测试NIC包验证完整流程
- `test_comprehensive.py` - 综合测试套件

### 端到端测试 (e2e/)
从用户角度出发，测试完整的用户场景和业务流程。

**特点**：
- 测试范围大、执行慢
- 模拟真实用户操作
- 验证系统满足业务需求

**示例**：
- 完整的文件扫描 → 验证 → 导出流程
- GUI/CLI 完整用户交互流程

## 📋 运行测试

### 运行所有测试
```bash
# 运行单元测试
python3 tests/unit/test_simple.py
python3 tests/unit/test_modules.py
python3 tests/unit/test_package_id.py

# 运行集成测试
python3 tests/integration/test_refactored_structure.py
python3 tests/integration/test_nic_validation.py
python3 tests/integration/test_scenario_validation.py
python3 tests/integration/test_comprehensive.py

# 运行端到端测试
python3 tests/e2e/test_*.py
```

### 运行特定测试
```bash
# 运行单个测试文件
python3 tests/unit/test_package_id.py
```

### 运行测试数据生成器
```bash
# 生成标准NIC包
python3 tests/shared/utils/test_data_generator/create_test_nic.py

# 生成匿名模式NIC包（用于测试匿名模式检测）
python3 tests/shared/utils/test_data_generator/create_anonymous_nic.py

# 生成短时间范围NIC包（用于测试时间范围检测）
python3 tests/shared/utils/test_data_generator/create_short_collect_range_nic.py

# 生成不支持的NE类型NIC包（用于测试NE类型支持）
python3 tests/shared/utils/test_data_generator/create_unsupported_nic.py
```

## 📊 测试覆盖度

- **当前覆盖度**: 约85-90%
- **单元测试**: 覆盖核心业务逻辑
- **集成测试**: 覆盖主要功能流程
- **测试用例数**: 21+ (持续增加)

详见 `docs/test-coverage-analysis.md` 和 `docs/test-summary.md`。

## 🔄 需求追踪

查看 `docs/requirements-mapping.md` 了解需求与测试用例的映射关系。

## 📝 编写新测试

### 1. 确定测试类型
- **单元测试**: 测试单个函数/类 → `unit/`
- **集成测试**: 测试多个模块协作 → `integration/`
- **E2E测试**: 测试完整用户场景 → `e2e/`

### 2. 命名规范
- 文件名: `test_<模块名>.py`
- 函数名: `test_<功能描述>`

### 3. 测试结构
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试描述
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_something():
    """测试某个功能"""
    # 准备测试数据
    # 执行测试
    # 断言结果
    assert result == expected
    print("✅ 测试通过")

if __name__ == "__main__":
    test_something()
```

## 🛠️ 共享测试工具

位于 `shared/utils/` 目录，包含：
- **test_data_generator/** - 测试数据生成器

## 📚 相关文档

- [测试覆盖度分析](docs/test-coverage-analysis.md)
- [测试总结报告](docs/test-summary.md)
- [需求-测试用例映射](docs/requirements-mapping.md)

## 🤝 贡献指南

1. 新增测试时，请遵循目录结构和命名规范
2. 提交前确保所有测试通过
3. 更新相关的测试文档
4. 新增测试用例时，更新 `requirements-mapping.md`

---

**最后更新**: 2026-03-10
