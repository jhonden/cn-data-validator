# 项目重构方案设计文档

## 📋 项目概述

本文档描述了从当前项目结构到新结构的重构方案，旨在提高代码组织的清晰度、可维护性和可扩展性。

## 🎯 重构目标

### 主要目标
1. **代码组织优化**：采用Java风格的包结构
2. **职责分离**：明确view、service、config层职责
3. **高内聚**：将相关的MML验证逻辑组织在一起
4. **可维护性**：便于后续功能扩展和维护

### 预期收益
- ✅ 代码结构更清晰
- ✅ 符合MVC架构模式
- ✅ 便于单元测试
- ✅ 便于团队协作
- ✅ 便于未来扩展

## 📁 重构前后结构对比

### 重构前结构
```
cn-data-validator/
├── src/
│   ├── validator_qt.py
│   ├── validator_cli.py
│   └── exceptions.py
├── utils/
│   ├── file_scanner.py
│   ├── package_identifier.py
│   ├── nic_validator.py
│   ├── static_mml_checker.py
│   ├── scenario_checker.py
│   ├── custom_validators/
│   ├── design_tokens.py
│   ├── typography.py
│   └── config files
```

### 重构后结构
```
cn-data-validator/
└── src/
    ├── view/
    │   ├── __init__.py
    │   ├── validator_qt.py     # PyQt6 GUI
    │   └── validator_cli.py    # CLI
    │
    ├── service/
    │   ├── __init__.py
    │   ├── file_scanner.py     # 文件扫描
    │   ├── package_identifier.py  # 包识别
    │   ├── nic_validator.py    # NIC验证主控制器
    │   └── scenario_checker.py    # 场景检查
    │
    ├── service/static_mml/
    │   ├── __init__.py
    │   ├── static_mml_checker.py  # 静态MML主检查器
    │   └── custom_validators/
    │       ├── __init__.py
    │       ├── vCG_validator.py
    │       ├── vUGW_validator.py
    │       ├── vUSN_validator.py
    │       └── USCDB_validator.py
    │
    ├── config/
    │   ├── static_mml_config.yaml
    │   └── scenario_config.yaml
    │
    ├── design_tokens.py         # UI设计令牌
    ├── typography.py            # 排版配置
    └── exceptions.py            # 公共异常
```

## 🔧 重构要求

### 1. 目录结构要求
- 所有Python源代码统一放在`src/`下
- 创建`view/`、`service/`、`config/`目录
- 在`service/`下创建`static_mml/`子目录
- 所有目录必须有`__init__.py`文件

### 2. 导入语句更新
- 所有import语句需要相应更新
- 使用相对导入或绝对导入（推荐）
- 确保重构后所有模块都能正常导入

### 3. 文件移动要求
- 文件内容保持不变
- 只改变文件位置和import路径
- 确保文件的执行逻辑不变

### 4. 配置文件处理
- YAML配置文件移到`config/`目录
- 确保所有文件读取路径正确

### 5. 脚本和文档更新
- 更新所有相关的运行脚本
- 更新文档中的路径引用
- 更新CLAUDE.md和README.md

## 📝 重构步骤

### 阶段1：准备阶段
1. 备份当前代码
2. 确认所有文件都能正常运行
3. 创建新的目录结构

### 阶段2：文件移动
1. 创建`view/`目录，移动GUI和CLI文件
2. 创建`service/`目录，移动核心业务逻辑文件
3. 创建`service/static_mml/`和`custom_validators/`
4. 创建`config/`目录，移动配置文件
5. 移动其他文件到合适位置

### 阶段3：代码更新
1. 更新所有import语句
2. 更新配置文件路径
3. 更新资源文件引用

### 阶段4：测试验证
1. 编写并运行核心测试用例
2. 验证各模块功能正常
3. 验证GUI和CLI正常工作

## 🧪 核心自测用例

### 1. 基础功能测试
**测试目的**：验证重构后基本功能正常
**测试步骤**：
- 测试文件扫描功能
- 测试包类型识别
- 测试基本的NIC包验证

**预期结果**：
- FileScanner能正常扫描目录
- PackageIdentifier能识别NIC包
- 基本的验证逻辑工作正常

### 2. GUI功能测试
**测试目的**：验证PyQt6 GUI正常工作
**测试步骤**：
- 启动validator_qt.py
- 选择包含NIC包的目录
- 执行扫描和验证
- 验证结果显示正确

**预期结果**：
- GUI启动无错误
- 能正常选择目录
- 扫描过程正常
- 结果表格显示正确

### 3. CLI功能测试
**测试目的**：验证命令行版本正常工作
**测试步骤**：
- 运行validator_cli.py
- 输入有效的NIC包目录
- 查看输出结果

**预期结果**：
- CLI启动无错误
- 能接收用户输入
- 输出格式正确
- 验证结果准确

### 4. 静态MML测试
**测试目的**：验证静态MML校验功能
**测试步骤**：
- 加载静态MML配置
- 测试不同NE类型的验证器
- 验证自定义验证器正常工作

**预期结果**：
- static_mml_config.yaml正确加载
- 各NE类型验证器工作正常
- 自定义验证器逻辑正确

### 5. 场景检查测试
**测试目的**：验证场景检查功能
**测试步骤**：
- 加载场景配置
- 测试NE场景匹配
- 验证场景参数格式

**预期结果**：
- scenario_config.yaml正确加载
- 场景匹配逻辑正确
- 参数格式验证正常

### 6. 配置文件测试
**测试目的**：验证配置文件读取
**测试步骤**：
- 测试static_mml_config.yaml
- 测试scenario_config.yaml
- 验证路径正确性

**预期结果**：
- 配置文件能正确读取
- 路径解析正确
- 配置项有效

## 📋 重构检查清单

### 重构完成条件
- [ ] 所有文件已移动到正确位置
- [ ] 所有import语句已更新
- [ ] 所有目录都有__init__.py
- [ ] 配置文件路径正确
- [ ] 运行脚本已更新
- [ ] 文档已更新
- [ ] 所有6个核心测试用例通过
- [ ] GUI和CLI都能正常启动
- [ ] 业务逻辑功能正常

### 验证清单
- [ ] python3 -m py_compile src/**/*.py 编译无错误
- [ ] python3 src/view/validator_qt.py 能正常启动
- [ ] python3 src/view/validator_cli.py 能正常运行
- [ ] 所有模块导入正常
- [ ] 配置文件能正常加载
- [ ] 测试脚本都能通过

## 🚨 注意事项

1. **备份**：重构前务必备份代码
2. **测试**：每个阶段都要进行充分测试
3. **文档**：及时更新相关文档
4. **依赖**：确保所有依赖关系正确
5. **性能**：重构后性能不应下降

## 🔄 回滚计划

如果重构失败，可以按以下步骤回滚：
1. 恢复备份的文件
2. 恢复原始的目录结构
3. 更新所有配置和文档

---

**文档版本**: 1.0
**创建日期**: 2026-03-10
**最后更新**: 2026-03-10
**负责人**: Claude Code