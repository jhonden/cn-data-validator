# 共享测试工具

本目录包含测试过程中可共享使用的工具、辅助函数和测试数据生成器。

## 📁 目录结构

```
tests/shared/
├── README.md                   # 本文档
└── utils/                     # 工具目录
    └── test_data_generator/    # 测试数据生成器
        ├── create_test_nic.py              # 创建标准NIC包
        ├── create_anonymous_nic.py          # 创建匿名模式NIC包
        ├── create_non_anonymous_nic.py      # 创建非匿名模式NIC包
        ├── create_short_collect_range_nic.py # 创建短时间范围NIC包
        ├── create_long_collect_range_nic.py  # 创建长时间范围NIC包
        └── create_unsupported_nic.py      # 创建不支持的NE类型NIC包
```

## 🛠️ 工具说明

### test_data_generator/

测试数据生成工具集合，用于创建各种测试场景的NIC包。

#### create_test_nic.py
**功能**：创建标准的、符合要求的NIC包

**使用方法**：
```bash
python3 tests/shared/utils/test_data_generator/create_test_nic.py
```

**生成的包特点**：
- 非匿名模式
- 采集时间范围 ≥ 24小时
- 包含支持的NE类型
- neinfo.txt 格式正确

**用途**：基本功能测试、正常流程测试

---

#### create_anonymous_nic.py
**功能**：创建匿名化采集的NIC包

**使用方法**：
```bash
python3 tests/shared/utils/test_data_generator/create_anonymous_nic.py
```

**生成的包特点**：
- 匿名模式（AnonymousAuthMode=true）
- 其他特征符合要求

**用途**：测试匿名模式检测功能（应验证失败）

---

#### create_non_anonymous_nic.py
**功能**：创建非匿名化采集的NIC包

**使用方法**：
```bash
python3 tests/shared/utils/test_data_generator/create_non_anonymous_nic.py
```

**生成的包特点**：
- 非匿名模式（AnonymousAuthMode=false）
- 其他特征符合要求

**用途**：测试正常NIC包

---

#### create_short_collect_range_nic.py
**功能**：创建采集时间范围小于24小时的NIC包

**使用方法**：
```bash
python3 tests/shared/utils/test_data_generator/create_short_collect_range_nic.py
```

**生成的包特点**：
- 采集时间范围 < 24小时
- 其他特征符合要求

**用途**：测试时间范围检测功能（应验证失败）

---

#### create_long_collect_range_nic.py
**功能**：创建采集时间范围大于24小时的NIC包

**使用方法**：
```bash
python3 tests/shared/utils/test_data_generator/create_long_collect_range_nic.py
```

**生成的包特点**：
- 采集时间范围 > 24小时
- 其他特征符合要求

**用途**：测试正常的NIC包

---

#### create_unsupported_nic.py
**功能**：创建包含全部不支持的NE类型的NIC包

**使用方法**：
```bash
python3 tests/shared/utils/test_data_generator/create_unsupported_nic.py
```

**生成的包特点**：
- 包含所有不支持的NE类型
- 其他特征符合要求

**用途**：测试NE类型支持检测功能（应验证失败）

---

## 🔧 扩展指南

### 添加新的测试数据生成器

1. 在 `utils/` 目录下创建新的Python脚本
2. 实现测试数据生成逻辑
3. 在本文件中添加文档说明
4. 更新相关的测试用例

### 添加共享的测试辅助函数

可以在 `utils/` 目录下创建新的模块，例如：
- `assert_helpers.py` - 断言辅助函数
- `mock_helpers.py` - Mock辅助函数
- `data_factory.py` - 数据工厂类

---

## 📝 使用示例

```python
# 在测试中使用生成的NIC包
import os
import tempfile
from src.service.nic_validator import NICValidator

def test_validation_with_generated_package():
    """使用生成的测试包进行测试"""
    # 生成测试包
    nic_path = "path/to/generated/nic.tar.gz"

    # 执行验证
    validator = NICValidator(nic_path)
    result = validator.validate()

    # 断言结果
    assert result['valid'] == True
```

---

## 🤝 贡献指南

1. 新的工具应该有清晰的文档说明
2. 工具应该遵循项目的编码规范
3. 使用 `if __name__ == "__main__"` 确保可以独立运行
4. 添加适当的错误处理和日志输出

---

**最后更新**: 2026-03-10
