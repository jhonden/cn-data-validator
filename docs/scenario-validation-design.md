# 网元采集场景校验 - 设计文档

> **创建日期**: 2026-03-08
> **版本**: v1.0.0
> **目的**: 记录网元采集场景校验功能的设计需求和规则

---

## 1. 背景与目标

### 1.1 背景说明

网元（NE）在采集数据时需要使用正确的采集场景（Collection Scenario）。不同的网元类型需要使用特定的采集场景，如果场景不匹配，会导致数据采集不完整或无法使用。

例如：
- 离线健康检查场景：适用于需要离线采集健康检查信息的网元
- 云巡检场景：适用于支持云巡检的网元
- 健康检查场景：适用于通用健康检查的网元

### 1.2 设计目标

1. 验证 NIC 包中每个网元的采集场景是否正确
2. 支持不同网元类型的不同场景要求
3. 采用配置化设计，便于后续扩展新网元类型
4. 提供清晰的错误定位和提示
5. 支持特殊网元类型（如 USCDB）的版本格式判断
6. 在 UI 中以网元为单位展示校验结果

---

## 2. 功能需求

### 2.1 核心功能

| 功能 | 描述 | 优先级 |
|------|------|--------|
| 场景读取 | 从 taskinfo.txt 读取采集场景信息 | P0 |
| 场景验证 | 验证实际场景与预期场景是否匹配 | P0 |
| 配置化规则 | 通过配置文件定义各网元类型的预期场景 | P0 |
| 特殊处理 | 支持 USCDB 根据版本格式动态确定预期场景 | P0 |
| 错误提示 | 提供清晰的场景错误提示信息 | P0 |

### 2.2 数据源说明

**taskinfo.txt 格式**：
```
scenario_group_name=Cloud health check scenario;
```

**NeAllinfos.xml 格式**（仅 USCDB 使用）：
```xml
<root>
  <NeInfo>
    <neVersion>23.1.0.18</neVersion>
    ...
  </NeInfo>
</root>
```

---

## 3. 校验流程

### 3.1 标准校验流程

```
1. 读取 NIC 包的 taskinfo.txt
   ↓
2. 解析 scenario_group_name=XXX; 获取实际场景
   ↓
3. 查询配置文件获取该网元类型的预期场景
   ↓
4. 比较实际场景与预期场景
   ↓
5. 如果不匹配 → 记录错误信息
```

### 3.2 USCDB 特殊校验流程

```
1. 读取网元文件夹的 NeAllinfos.xml
   ↓
2. 解析 <neVersion> 标签获取版本号
   ↓
3. 判断版本格式：
   - VRC 格式：V500R020C10（以 V 开头，后接数字字母）
   - 点分格式：23.1.0.18（包含点号）
   ↓
4. 根据版本格式确定预期场景：
   - VRC 格式 → "Offline health check scenario"
   - 点分格式 → "Cloud health check scenario"
   ↓
5. 读取 taskinfo.txt 获取实际场景
   ↓
6. 比较实际场景与预期场景
   ↓
7. 如果不匹配 → 记录错误信息
```

---

## 4. 配置文件结构

### 4.1 配置文件位置

**文件路径**: `utils/scenario_config.yaml`

### 4.2 配置文件格式

```yaml
scenarios:
  # 网元类型配置
  CSCF:
    en: Offline health check scenario
    zh: 离线健康检查信息收集场景

  ATS:
    en: Offline health check scenario
    zh: 离线健康检查信息收集场景

  # ... 其他网元类型

error_messages:
  scenario_mismatch:
    en: 'Collection scenario error: NE ''{ne_name}'' ({ne_type}) should use ''{expected_scenario}'' collection scenario'
    zh: 网元采集场景错误：网元'{ne_name}'（{ne_type}）应该使用'{expected_scenario}'采集场景
```

### 4.3 配置字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|--------|------|
| scenarios | dict | 是 | 采集场景配置字典 |
| scenarios.{ne_type}.en | string | 是 | 英文场景名称 |
| scenarios.{ne_type}.zh | string | 是 | 中文场景名称 |
| error_messages | dict | 是 | 错误消息模板 |
| ui_language | string | 否 | UI 语言：en/zh（默认 en） |

---

## 5. 网元类型场景规则

### 5.1 离线健康检查信息收集场景

| 网元类型 | 英文场景名称 | 中文场景名称 | 配置键名 |
|---------|-------------|-------------|---------|
| CSCF | Offline health check scenario | 离线健康检查信息收集场景 | CSCF |
| ATS | Offline health check scenario | 离线健康检查信息收集场景 | ATS |
| CCF | Offline health check scenario | 离线健康检查信息收集场景 | CCF |
| SE2900 | Offline health check scenario | 离线健康检查信息收集场景 | SE2900 |
| CloudSE2980 | Offline health check scenario | 离线健康检查信息收集场景 | CloudSE2980 |
| HSS9860 | Offline health check scenario | 离线健康检查信息收集场景 | HSS9860 |
| UPCC | Offline health check scenario | 离线健康检查信息收集场景 | UPCC |
| SPSV3 | Offline health check scenario | 离线健康检查信息收集场景 | SPSV3 |
| USCDB | 离线健康检查信息收集场景 | 离线健康检查信息收集场景 | USCDB (VRC格式) |

### 5.2 云巡检场景

| 网元类型 | 英文场景名称 | 中文场景名称 | 配置键名 |
|---------|-------------|-------------|---------|
| UNC | Cloud health check scenario | 云巡检场景 | UNC |
| UDG | Cloud health check scenario | 云巡检场景 | UDG |
| USCDB (点分格式) | Cloud health check scenario | 云巡检场景 | USCDB (动态) |
| USC | Cloud health check scenario | 云巡检场景 | USC |
| UPCF | Cloud health check scenario | 云巡检场景 | UPCF |

### 5.3 健康检查场景

| 网元类型 | 英文场景名称 | 中文场景名称 | 配置键名 |
|---------|-------------|-------------|---------|
| vCG | Health check scenario | 健康检查场景 | vCG |
| vUGW | Health check scenario | 健康检查场景 | vUGW |
| vUSN | Health check scenario | 健康检查场景 | vUSN |

### 5.4 云巡检信息收集场景

| 网元类型 | 英文场景名称 | 中文场景名称 | 配置键名 |
|---------|-------------|-------------|---------|
| ENS | Cloud-based Inspection scenario | 云巡检信息收集场景 | ENS |

---

## 6. USCDB 特殊处理逻辑

### 6.1 版本格式判断

**VRC 格式**：
- 格式示例：V500R020C10、V500R023C10SPC110
- 特征：
  - 以字母 'V' 开头
  - 后接数字
  - 中间包含字母（如 R、C）
  - 后接更多数字
- 正则表达式：`^V\d+[A-Za-z]\d+`

**点分格式**：
- 格式示例：23.1.0.18、20.3.2
- 特征：
  - 包含点号 '.'
  - 通常为 3-4 段数字
- 判断逻辑：版本号中包含点号

### 6.2 场景映射规则

| 版本格式 | 预期场景（英文） | 预期场景（中文） |
|---------|-----------------|-----------------|
| VRC 格式 | Offline health check scenario | 离线健康检查信息收集场景 |
| 点分格式 | Cloud health check scenario | 云巡检场景 |
| 未知格式 | Offline health check scenario | 离线健康检查信息收集场景（默认）|

### 6.3 数据来源

**文件路径**: `{网元文件夹}/NeAllinfos.xml`

**XML 结构示例**：
```xml
<root>
  <NeInfo>
    <BeginTime>2025-02-12 15:50:57</BeginTime>
    <EndTime>2025-02-19 15:50:57</EndTime>
    <adaptVersion>iManagerOSS_UDM_MATCHENG_23.1.0.18</adaptVersion>
    <Fdn>NE=690</Fdn>
    <neName>UDM-FE-TBS1</neName>
    <neTypeId>9588</neTypeId>
    <neVersion>23.1.0.18</neVersion>  <!-- 这里的版本号用于判断格式 -->
    <ip>10.37.125.193</ip>
    ...
  </NeInfo>
</root>
```

### 6.4 校验示例

**示例 1：VRC 格式版本**
```
网元: USCDB_NE=1_IP_10_140_1_1_PPR_USCDB01
版本: V500R020C10
预期场景: Offline health check scenario
实际场景: Offline health check scenario
结果: 通过 ✓
```

**示例 2：点分格式版本**
```
网元: USCDB_NE=2_IP_10_140_2_1_PPR_USCDB02
版本: 23.1.0.18
预期场景: Cloud health check scenario
实际场景: Cloud health check scenario
结果: 通过 ✓
```

**示例 3：场景不匹配**
```
网元: USCDB_NE=2_IP_10_140_2_1_PPR_USCDB02
版本: 23.1.0.18
预期场景: Cloud health check scenario
实际场景: Offline health check scenario
结果: 失败 ✗
错误: Collection scenario error: NE 'USCDB02' (USCDB) should use 'Cloud health check scenario' collection scenario
```

---

## 7. 校验结果结构

### 7.1 单个网元校验结果

```python
{
    'ne_name': str,              # 网元名称
    'ne_type': str,              # 网元类型
    'valid': True/False,         # 校验是否通过
    'expected_scenario': str,     # 预期场景名称
    'actual_scenario': str,       # 实际场景名称（从 taskinfo.txt 读取）
    'error': str or None         # 错误消息（如果校验失败）
}
```

### 7.2 所有网元校验结果汇总

```python
{
    'total_ne_count': int,       # 网元总数
    'valid_ne_count': int,       # 校验通过的网元数
    'invalid_ne_count': int,     # 校验失败的网元数
    'ne_results': List[Dict]     # 每个网元的详细结果
}
```

---

## 8. 代码架构设计

### 8.1 文件结构

```
utils/
├── scenario_checker.py           # 场景校验器（独立类）
├── static_mml_checker.py        # 静态 MML 校验器（独立类）
└── scenario_config.yaml          # 场景配置文件
```

### 8.2 类设计

```python
# utils/scenario_checker.py

class ScenarioChecker:
    """采集场景校验器"""

    def __init__(self, config_path: str):
        """
        初始化检查器，加载配置

        Args:
            config_path: 场景配置文件路径 (scenario_config.yaml)
        """
        self.config_path = config_path
        self.config = self._load_config()

    def check_package(self, ne_parent_path: str, ne_instances: List) -> Dict:
        """
        检查整个包的所有网元

        Args:
            ne_parent_path: 网元数据文件夹路径
            ne_instances: 网元实例列表

        Returns:
            {
                'total_ne_count': int,
                'valid_ne_count': int,
                'invalid_ne_count': int,
                'ne_results': List[Dict]
            }
        """

    def _check_ne(self, ne_parent_path: str, ne_instance) -> Dict:
        """
        检查单个网元

        Returns:
            {
                'ne_name': str,
                'ne_type': str,
                'valid': True/False,
                'expected_scenario': str,
                'actual_scenario': str,
                'error': str or None
            }
        """

    def _get_uscdb_expected_scenario(self, ne_folder_path: str) -> Optional[str]:
        """
        获取 USCDB 的预期场景（基于版本格式）

        Returns:
            预期场景名称，如果无法确定则返回 None
        """

    def _read_scenario_from_taskinfo(self, ne_parent_path: str) -> Optional[str]:
        """
        从 taskinfo.txt 读取场景名称

        Returns:
            场景名称，如果未找到则返回 None
        """

    def _format_scenario_error(self, ne_type: str, ne_name: str,
                             expected_scenario: str, actual_scenario: str) -> str:
        """
        格式化场景错误消息

        Returns:
            格式化的错误消息（支持中英文）
        """
```

### 8.3 架构设计原则

1. **单一职责原则**：
   - `ScenarioChecker`：只负责采集场景校验
   - `StaticMMLChecker`：只负责静态 MML 配置校验
   - 两个校验器完全独立，互不干扰

2. **配置驱动**：
   - 所有网元类型的场景规则通过配置文件定义
   - 新增网元类型只需修改配置文件，无需修改代码

3. **可扩展性**：
   - 支持添加新的校验器（如新增校验类型）
   - 支持自定义特殊网元的校验逻辑

4. **国际化支持**：
   - 配置文件支持中英双语
   - 错误消息根据 UI 语言配置显示对应语言

---

## 9. 与静态 MML 校验的集成

### 9.1 校验流程集成

```
NICValidator.validate()
    ↓
├─ NICValidator._check_ne_folders()
├─ NICValidator._check_collect_range()
├─ NICValidator._check_anonymous_mode()
├─ NICValidator._check_static_mml()  ← 调用两个校验器
│   ├─ StaticMMLChecker.check_package()
│   └─ ScenarioChecker.check_package()
└─ NICValidator._check_required_files()
```

### 9.2 结果合并

校验结果存储在 `nic_validation` 字典的不同键中：

```python
{
    'static_mml_validation': {
        # 静态 MML 校验结果
        'total_ne_count': 5,
        'valid_ne_count': 3,
        'invalid_ne_count': 2,
        'ne_results': [...]
    },
    'scenario_validation': {
        # 采集场景校验结果
        'total_ne_count': 5,
        'valid_ne_count': 4,
        'invalid_ne_count': 1,
        'ne_results': [...]
    }
}
```

### 9.3 UI 显示

在详情面板中，同时显示两种校验结果：

```
Network Element Details (5 total)
┌──────────────────────────────────────────────────────────────────┐
│ [✓] NE1 (CSCF_NE=1094)                Pass             │
│     ✓ Static MML: ALLME_CSCF.txt (dataconfiguration/)      │
│     ✓ Scenario: Offline health check scenario                │
│                                                                 │
│ [⚠️] NE2 (USCDB_NE=1)                       Fail             │
│     ✓ Static MML: valid                                  │
│     ⚠️ Scenario: Should use 'Cloud health check scenario'   │
│     Actual: Offline health check scenario                  │
│                                                                 │
│ [✗] NE3 (ATS_NE=1044)                       Fail             │
│     ⚠️ Static MML: dataconfiguration/*.tar.gz (missing)   │
│     ✓ Scenario: Offline health check scenario                │
└──────────────────────────────────────────────────────────────────┘

Summary: Total: 5 | Pass: 2 | Warning: 0 |
         Static MML Fail: 1 | Scenario Fail: 1
```

---

## 10. 错误提示信息

### 10.1 错误消息格式

**英文格式**：
```
Collection scenario error: NE 'NE_NAME' (NE_TYPE) should use 'EXPECTED_SCENARIO' collection scenario
```

**中文格式**：
```
网元采集场景错误：网元'NE_NAME'（NE_TYPE）应该使用'EXPECTED_SCENARIO'采集场景
```

### 10.2 错误场景示例

**场景 1：普通网元场景不匹配**
```
实际: Cloud health check scenario
预期: Offline health check scenario
错误: Collection scenario error: NE 'ATS01' (ATS) should use 'Offline health check scenario' collection scenario
```

**场景 2：USCDB VRC 格式版本使用了错误场景**
```
版本: V500R020C10 (VRC 格式)
预期: Offline health check scenario
实际: Cloud health check scenario
错误: Collection scenario error: NE 'USCDB01' (USCDB) should use 'Offline health check scenario' collection scenario
```

**场景 3：USCDB 点分格式版本使用了错误场景**
```
版本: 23.1.0.18 (点分格式)
预期: Cloud health check scenario
实际: Offline health check scenario
错误: Collection scenario error: NE 'USCDB02' (USCDB) should use 'Cloud health check scenario' collection scenario
```

---

## 11. 测试用例

### 11.1 标准网元场景校验

#### 用例 ID：SC-T-001 - CSCF 场景匹配

| 项目 | 说明 |
|------|------|
| **网元类型** | CSCF |
| **测试场景** | 正常情况 - 场景匹配 |
| **taskinfo.txt** | `scenario_group_name=Offline health check scenario;` |
| **预期结果** | Status: Valid (通过) |
| **验证步骤** | 1. 选择包含 CSCF_NE=1094 的 NIC 包<br>2. 检查校验结果中的 valid=True |

---

#### 用例 ID：SC-T-002 - CSCF 场景不匹配

| 项目 | 说明 |
|------|------|
| **网元类型** | CSCF |
| **测试场景** | 异常情况 - 场景不匹配 |
| **taskinfo.txt** | `scenario_group_name=Cloud health check scenario;` |
| **预期结果** | Status: Invalid (失败)<br>Error: "Collection scenario error: NE 'CSCF01' (CSCF) should use 'Offline health check scenario' collection scenario" |
| **验证步骤** | 1. 选择包含 CSCF_NE=1094 的 NIC 包<br>2. 检查校验结果中的 valid=False<br>3. 检查 error 字段包含正确的错误消息 |

---

### 11.2 USCDB 特殊场景校验

#### 用例 ID：SC-T-101 - USCDB VRC 格式，场景匹配

| 项目 | 说明 |
|------|------|
| **网元类型** | USCDB |
| **版本格式** | VRC |
| **NeAllinfos.xml** | `<neVersion>V500R020C10</neVersion>` |
| **taskinfo.txt** | `scenario_group_name=Offline health check scenario;` |
| **预期结果** | Status: Valid (通过)<br>Expected: Offline health check scenario |
| **验证步骤** | 1. 选择包含 USCDB_NE=1 的 NIC 包<br>2. 检查 NeAllinfos.xml 中版本为 V500R020C10<br>3. 检查校验结果中的 valid=True<br>4. 检查 expected_scenario=Offline health check scenario |

---

#### 用例 ID：SC-T-102 - USCDB 点分格式，场景匹配

| 项目 | 说明 |
|------|------|
| **网元类型** | USCDB |
| **版本格式** | 点分 |
| **NeAllinfos.xml** | `<neVersion>23.1.0.18</neVersion>` |
| **taskinfo.txt** | `scenario_group_name=Cloud health check scenario;` |
| **预期结果** | Status: Valid (通过)<br>Expected: Cloud health check scenario |
| **验证步骤** | 1. 选择包含 USCDB_NE=2 的 NIC 包<br>2. 检查 NeAllinfos.xml 中版本为 23.1.0.18<br>3. 检查校验结果中的 valid=True<br>4. 检查 expected_scenario=Cloud health check scenario |

---

#### 用例 ID：SC-T-103 - USCDB VRC 格式，场景不匹配

| 项目 | 说明 |
|------|------|
| **网元类型** | USCDB |
| **版本格式** | VRC |
| **NeAllinfos.xml** | `<neVersion>V500R020C10</neVersion>` |
| **taskinfo.txt** | `scenario_group_name=Cloud health check scenario;` |
| **预期结果** | Status: Invalid (失败)<br>Expected: Offline health check scenario<br>Error: 场景不匹配错误消息 |
| **验证步骤** | 1. 选择包含 USCDB_NE=1 的 NIC 包<br>2. 检查版本为 VRC 格式，预期应为 Offline<br>3. 检查实际为 Cloud，校验失败<br>4. 检查 error 字段包含错误消息 |

---

### 11.3 综合测试用例

| 用例ID | 网元类型 | 场景 | 预期 | 测试状态 |
|--------|---------|------|------|---------|
| SC-T-001 | CSCF | 场景匹配 | Pass | 待执行 |
| SC-T-002 | CSCF | 场景不匹配 | Fail | 待执行 |
| SC-T-003 | ATS | 场景匹配 | Pass | 待执行 |
| SC-T-004 | UDG | 场景匹配 | Pass | 待执行 |
| SC-T-005 | vCG | 场景匹配 | Pass | 待执行 |
| SC-T-006 | vUGW | 场景匹配 | Pass | 待执行 |
| SC-T-007 | vUSN | 场景匹配 | Pass | 待执行 |
| SC-T-008 | HSS9860 | 场景匹配 | Pass | 待执行 |
| SC-T-009 | ENS | 场景匹配 | Pass | 待执行 |
| SC-T-010 | UPCC | 场景匹配 | Pass | 待执行 |
| SC-T-011 | UPCF | 场景匹配 | Pass | 待执行 |
| SC-T-012 | SPSV3 | 场景匹配 | Pass | 待执行 |
| SC-T-013 | USC | 场景匹配 | Pass | 待执行 |
| SC-T-101 | USCDB (VRC) | 场景匹配 | Pass | 待执行 |
| SC-T-102 | USCDB (点分) | 场景匹配 | Pass | 待执行 |
| SC-T-103 | USCDB (VRC) | 场景不匹配 | Fail | 待执行 |
| SC-T-104 | USCDB (点分) | 场景不匹配 | Fail | 待执行 |

---

## 12. 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|---------|
| v1.0.0 | 2026-03-08 | 初始版本，完成采集场景校验功能设计和实现 |

---

## 13. 附录

### 13.1 完整的网元类型场景配置表

| 网元类型 | 英文场景名称 | 中文场景名称 | 配置键名 | 特殊处理 |
|---------|-------------|-------------|---------|---------|
| CSCF | Offline health check scenario | 离线健康检查信息收集场景 | CSCF | 否 |
| ATS | Offline health check scenario | 离线健康检查信息收集场景 | ATS | 否 |
| CCF | Offline health check scenario | 离线健康检查信息收集场景 | CCF | 否 |
| SE2900 | Offline health check scenario | 离线健康检查信息收集场景 | SE2900 | 否 |
| CloudSE2980 | Offline health check scenario | 离线健康检查信息收集场景 | CloudSE2980 | 否 |
| HSS9860 | Offline health check scenario | 离线健康检查信息收集场景 | HSS9860 | 否 |
| UPCC | Offline health check scenario | 离线健康检查信息收集场景 | UPCC | 否 |
| SPSV3 | Offline health check scenario | 离线健康检查信息收集场景 | SPSV3 | 否 |
| UNC | Cloud health check scenario | 云巡检场景 | UNC | 否 |
| UDG | Cloud health check scenario | 云巡检场景 | UDG | 否 |
| USC | Cloud health check scenario | 云巡检场景 | USC | 否 |
| UPCF | Cloud health check scenario | 云巡检场景 | UPCF | 否 |
| vCG | Health check scenario | 健康检查场景 | vCG | 否 |
| vUGW | Health check scenario | 健康检查场景 | vUGW | 否 |
| vUSN | Health check scenario | 健康检查场景 | vUSN | 否 |
| ENS | Cloud-based Inspection scenario | 云巡检信息收集场景 | ENS | 否 |
| USCDB | 动态确定 | 动态确定 | USCDB | **是（版本格式判断）** |

### 13.2 USCDB 版本格式正则表达式

**VRC 格式**：
```regex
^V\d+[A-Za-z]\d+
```

**匹配示例**：
- ✓ V500R020C10
- ✓ V500R023C10SPC110
- ✓ V123R456C789

**不匹配示例**：
- ✗ 23.1.0.18
- ✗ 20.3.2
- ✗ v500r020c10 (小写)

### 13.3 配置文件更新指南

当需要新增网元类型时，按以下步骤更新 `scenario_config.yaml`：

1. 在 `scenarios` 节下添加新网元类型配置
2. 添加 `en` 字段（英文场景名称）
3. 添加 `zh` 字段（中文场景名称）
4. 保存文件
5. 无需修改代码，配置自动生效

**示例**：
```yaml
scenarios:
  # ... 现有配置
  NEW_NE_TYPE:
    en: New Scenario Name
    zh: 新场景名称
```

---

**文档维护者**: Claude AI Assistant
**最后更新**: 2026-03-08
**下次更新**: 新增网元类型或修改校验规则时更新
