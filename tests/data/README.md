# 测试数据目录

本目录包含项目测试所需的各种测试数据。

## 📁 目录结构

```
tests/data/
├── README.md                   # 本文档
├── test_data/                  # 通用测试数据
│   └── (各种测试数据文件)
└── test_packages/              # 测试包样本
    ├── (标准NIC包样本)
    ├── (匿名模式包样本)
    ├── (短时间范围包样本)
    └── (不支持的NE类型包样本)
```

## 📦 测试数据说明

### test_data/
通用测试数据文件，包括：
- 配置文件样本
- 测试XML文件
- 测试文本文件
- 其他辅助测试数据

### test_packages/
网络包样本，用于测试各种场景：
- **标准NIC包** - 正常的NIC包，用于基本功能测试
- **匿名模式包** - 匿名化采集的NIC包，用于测试匿名模式检测（应失败）
- **短时间范围包** - 采集时间范围<24小时的NIC包，用于测试时间范围检测（应失败）
- **不支持的NE类型包** - 包含所有不支持的NE类型的NIC包，用于测试NE类型支持（应失败）

## 🛠️ 生成测试数据

使用 `shared/utils/test_data_generator/` 中的脚本生成测试数据：

```bash
# 生成标准NIC包
python3 tests/shared/utils/test_data_generator/create_test_nic.py

# 生成匿名模式包
python3 tests/shared/utils/test_data_generator/create_anonymous_nic.py

# 生成短时间范围包
python3 tests/shared/utils/test_data_generator/create_short_collect_range_nic.py

# 生成不支持的NE类型包
python3 tests/shared/utils/test_data_generator/create_unsupported_nic.py
```

## 📝 添加新的测试数据

1. 将数据文件放入 `test_data/` 或 `test_packages/` 目录
2. 在本文件中添加说明
3. 在对应的测试代码中引用数据文件
4. 更新 `../docs/requirements-mapping.md` 如果涉及新的需求测试

## ⚠️ 注意事项

1. **不要提交大文件** - 避免将大型二进制文件提交到代码仓库
2. **敏感数据** - 确保测试数据不包含真实的敏感信息
3. **版本控制** - 测试数据应该有清晰的版本标识
4. **文档化** - 每个测试数据都应该有对应的说明

## 🔧 维护建议

- 定期清理过时的测试数据
- 保持测试数据与实际使用场景一致
- 使用脚本自动生成测试数据，避免手动创建
- 为复杂的测试数据添加说明文档

---

**最后更新**: 2026-03-10
