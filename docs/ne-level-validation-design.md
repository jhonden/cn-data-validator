# 网元级别校验功能 - 需求设计文档

> **创建日期**: 2026-03-07
> **版本**: v0.1.0
> **目的**: 记录网元级别静态 MML 配置校验功能的设计需求

---

## 1. 背景与目标

### 1.1 背景说明

当前 NIC 包校验是在包级别进行的，一个 NIC 包可能包含多个网元。不同网元的校验状态可能不同：
- 网元 A：校验通过（Valid）
- 网元 B：校验警告（Warning）- 缺少某些文件
- 网元 C：校验失败（Invalid）- 缺少关键配置

当前的包级别校验无法区分不同网元的状态，用户难以快速定位具体哪个网元有问题。

### 1.2 设计目标

1. 实现网元级别的静态 MML 配置检查
2. 支持不同网元类型的不同配置规则
3. 采用配置化设计，便于后续扩展新网元类型
4. 提供清晰的错误定位和提示
5. 在 UI 中以网元为单位展示校验结果

---

## 2. 功能需求

### 2.1 核心功能

| 功能 | 描述 | 优先级 |
|------|------|--------|
| 网元级别静态 MML 检查 | 检查每个网元是否包含静态 MML 配置文件 | P0 |
| 多网元类型支持 | 支持不同网元类型的不同文件路径和命名规则 | P0 |
| 配置化规则引擎 | 通过配置文件定义校验规则，无需修改代码 | P0 |
| 三种匹配模式 | 支持 any、all、custom 三种校验模式 | P0 |
| 自定义校验器 | 支持特殊网元类型的自定义校验逻辑 | P0 |

### 2.2 非功能需求

| 需求 | 说明 |
|------|------|
| 不校验的网元类型 | 支持某些网元类型不需要校验静态 MML（如 CSP、CGPOMU） |
| 部署形态判断 | vUGW 等网元有三种部署形态，需要自动判断 |
| 文件名大小写敏感 | 文件名匹配需要区分大小写 |

---

## 3. 校验规则模式

### 3.1 Match Mode: any（任意模式）

**描述**：任意一种格式的文件存在即通过

**适用场景**：大多数网元类型，静态 MML 存放在同一个目录下，文件名有多种格式

**配置示例**：
```yaml
ATS:
  path: "dataconfiguration"
  patterns:
    - "*.tar.gz"
    - "*.zip"
    - "ALLME_*.txt"
  match_mode: "any"
  required: true
```

**判断逻辑**：
- 遍历所有 patterns
- 只要找到一个匹配的文件 → 校验通过
- 所有 patterns 都没有匹配 → 校验失败

---

### 3.2 Match Mode: all（全部模式）

**描述**：所有格式的文件都必须存在才通过

**适用场景**：某些网元类型，每种格式的文件都必须有

**配置示例**：
```yaml
EXAMPLE_NE:
  path: "config/mml"
  patterns:
    - "static_mml.txt"
    - "dynamic_mml.txt"
  match_mode: "all"
  required: true
```

**判断逻辑**：
- 遍历所有 patterns
- 每种 pattern 都必须有匹配的文件
- 任一种 pattern 没有匹配 → 校验失败

---

### 3.3 Match Mode: custom（自定义模式）

**描述**：使用自定义校验算法进行复杂校验

**适用场景**：特殊网元类型，有复杂的校验逻辑（如 vUGW 的三种部署形态）

**配置示例**：
```yaml
vUGW:
  match_mode: "custom"
  custom_validator: "vUGW_validator"
  required: true
```

**判断逻辑**：
- 动态加载指定的自定义校验器模块
- 调用自定义校验器的 `validate_static_mml()` 函数
- 由自定义校验器实现复杂逻辑

---

## 4. 配置文件结构

### 4.1 配置文件格式

```yaml
# utils/static_mml_config.yaml

# 静态 MML 校验规则配置
static_mml_rules:
  # 网元类型配置（后续按需添加）

  # 示例1：普通网元类型（any 模式）
  ATS:
    path: "dataconfiguration"
    patterns:
      - "*.tar.gz"
      - "*.zip"
      - "ALLME_*.txt"
    match_mode: "any"
    required: true
    description: "Static MML Configuration"

  CSCF:
    path: "dataconfiguration"
    patterns:
      - "*.tar.gz"
      - "*.zip"
      - "ALLME_*.txt"
    match_mode: "any"
    required: true
    description: "Static MML Configuration"

  UDG:
    path: "configuration/static"
    patterns:
      - "static_mml.txt"
    match_mode: "any"
    required: true
    description: "Static MML Configuration"

  # 示例2：特殊网元类型（custom 模式）
  vUGW:
    match_mode: "custom"
    custom_validator: "vUGW_validator"
    required: true
    description: "Static MML Configuration (vUGW)"

  # 示例3：不需要校验的网元类型
  CSP:
    required: false
    description: "Static MML not required for CSP"
  CGPOMU:
    required: false
    description: "Static MML not required for CGPOMU"

---

## 4. 配置文件示例（完整）

```yaml
# utils/static_mml_config.yaml

# 静态 MML 校验规则配置
static_mml_rules:
  # 普通网元类型（使用 any 模式）
  ATS:
    path: "dataconfiguration"
    patterns:
      - "*.tar.gz"
      - "*.zip"
      - "ALLME_*.txt"
    match_mode: "any"
    required: true
    description: "Static MML Configuration"

  CSCF:
    path: "dataconfiguration"
    patterns:
      - "*.tar.gz"
      - "*.zip"
      - "ALLME_*.txt"
    match_mode: "any"
    required: true
    description: "Static MML Configuration"

  UDG:
    path: "configuration/static"
    patterns:
      - "static_mml.txt"
    match_mode: "any"
    required: true
    description: "Static MML Configuration"

  # 示例2：特殊网元类型（custom 模式）
  vUGW:
    match_mode: "custom"
    custom_validator: "vUGW_validator"
    required: true
    description: "Static MML Configuration (vUGW - 3 deployment modes)"
    note: "Auto-detect CGW/DGW/UGW deployment from subdirectories"

  # 示例3：不需要校验的网元类型
  CSP:
    required: false
    description: "Static MML not required for CSP"
  CGPOMU:
    required: false
    description: "Static MML not required for CGPOMU"

  # 云化网元类型（使用 any/all 模式）
  CloudCGW:
    path: "omo/mml"
    patterns:
      - "*.txt"
    match_mode: "all"
    required: true
    description: "Static MML Configuration (CGW deployment)"

  CloudDGW:
    path: "omo/mml"
    patterns:
      - "*.txt"
    match_mode: "all"
    required: true
    description: "Static MML Configuration (DGW deployment)"

  CloudUGW:
    path: "omo/mml"
    patterns:
      - "*.txt"
    match_mode: "all"
    required: true
    description: "Static MML Configuration (UGW deployment)"

  CloudUSN:
    path: ""
    patterns:
      - "omo/mml/*.txt"
      - "vnrs/mml/*.txt"
    match_mode: "any"
    required: true
    description: "Static MML Configuration"

  CloudSE2980:
    path: "dataconfiguration"
    patterns:
      - "*.txt"
    match_mode: "any"
    required: true
    description: "Static MML Configuration"

  SE2900:
    path: "dataconfiguration"
    patterns:
      - "*.zip"
    match_mode: "any"
    required: true
    description: "Static MML Configuration"

  CCF:
    path: "dataconfiguration"
    patterns:
      - "*.tar.gz"
    match_mode: "any"
    required: true
    description: "Static MML Configuration"

  SPSV3:
    path: "dataconfiguration"
    patterns:
      - "*.zip"
    match_mode: "any"
    required: true
    description: "Static MML Configuration"

  USC:
    path: "dataconfiguration"
    patterns:
      - "*.tar.gz"
    match_mode: "any"
    required: true
    description: "Static MML Configuration"

  HSS9860:
    path: "dataconfiguration"
    patterns:
      - "*.tar.gz"
    match_mode: "any"
    required: true
    description: "Static MML Configuration"

  UDM:
    path: "dataconfiguration"
    patterns:
      - "*.tar.gz"
    match_mode: "any"
    required: true
    description: "Static MML Configuration"

  UPCC:
    path: "dataconfiguration"
    patterns:
      - "*.tar.gz"
    match_mode: "any"
    required: true
    description: "Static MML Configuration"

  UPCF:
    path: "dataconfiguration"
    patterns:
      - "*.tar.gz"
    match_mode: "any"
    required: true
    description: "Static MML Configuration"

  ENS:
    path: "dataconfiguration"
    patterns:
      - "*.tar.gz"
    match_mode: "any"
    required: true
    description: "Static MML Configuration"

  USCDB:
    path: "uscdb/dataconfiguration"
    patterns:
      - "*.tar.gz"
    match_mode: "any"
    required: true
    description: "Static MML Configuration"

  ICG9815:
    path: "dataconfiguration"
    patterns:
      - "*.tar.gz"
    match_mode: "any"
    required: true
    description: "Static MML Configuration"

  ICG9816:
    path: "dataconfiguration"
    patterns:
      - "*.tar.gz"
    match_mode: "any"
    required: true
    description: "Static MML Configuration"

  # 待补充的网元类型
  vCG:
    path: "cgw/mml"
    patterns: ["*.txt"]
    required: false
    description: "Static MML not required for vCG"
    note: "Configuration pending"

  vUSN:
    path: ""
    patterns: []
    required: false
    description: "Static MML not required for vUSN"
    note: "Configuration pending"
```
  CSP:
    required: false
    description: "Static MML not required for CSP"

  CGPOMU:
    required: false
    description: "Static MML not required for CGPOMU"
```

### 4.2 配置字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|--------|------|
| path | string | 否 | 相对路径（相对于网元数据文件夹） |
| patterns | list[string] | 否 | 文件名匹配模式列表，支持通配符 `*` |
| match_mode | enum | 否 | 匹配模式：`any`/`all`/`custom` |
| custom_validator | string | 否 | 自定义校验器名称（match_mode=custom 时必填） |
| required | boolean | 否 | 该网元类型是否必须校验（默认 true） |
| description | string | 否 | 描述信息，用于 UI 显示 |

---

## 5. 特殊网元类型规则

### 5.1 vUGW 网元

**特性**：
- 有三种部署形态：CGW / DGW / UGW
- 每种部署形态有不同的 MML 配置文件要求

**部署形态判断**：
- 通过检查网元数据文件夹下的子目录名称判断
- 如果存在 `cgw/` → CGW 形态
- 如果存在 `dgw/` → DGW 形态
- 如果存在 `ugw/` → UGW 形态
- **注意**：不会同时存在多种形态的文件夹

**CGW 形态要求**：
```
{网元数据文件夹}/
├── omo/mml/*.txt
├── cgw/mml/mmlconf_cgw_*.txt
└── vnrs/mml/*.txt

校验规则：三个路径的文件都必须存在
```

**DGW 形态要求**：
```
{网元数据文件夹}/
├── omo/mml/*.txt
├── dgw/mml/mmlconf_dgw_*.txt
└── vnrs/mml/*.txt

校验规则：三个路径的文件都必须存在
```

**UGW 形态要求**：
```
{网元数据文件夹}/
├── omo/mml/*.txt
├── ugw/mml/mmlconf_ugw_*.txt
└── vnrs/mml/*.txt

校验规则：三个路径的文件都必须存在
```

**判断逻辑**：
- 三种部署形态中，有一套完整就算通过
- 部署模式名称（CGW/DGW/UGW）不呈现给用户

---

## 5.5 特殊网元类型规则

### vUGW 网元详细规则

**三种部署形态**：

| 部署形态 | 子目录 | 路径 | 说明 |
|----------|--------|------|------|
| CloudCGW | cgw/ | {网元数据文件夹}/cgw/mml/*.txt | CGW 形态 |
| CloudDGW | dgw/ | {网元数据文件夹}/dgw/mml/*.txt | DGW 形态 |
| CloudUGW | ugw/ | {网元数据文件夹}/ugw/mml/*.txt | UGW 形态 |

**CGW 形态详细配置**：
```
路径: {网元数据文件夹}/cgw/mml
patterns:
  - omo/mml/*.txt
  - cgw/mml/mmlconf_cgw_*.txt
  - vnrs/mml/*.txt
required: all（三个路径都必须有文件）
```

**DGW 形态详细配置**：
```
路径: {网元数据文件夹}/dgw/mml
patterns:
  - omo/mml/*.txt
  - dgw/mml/mmlconf_dgw_*.txt
  - vnrs/mml/*.txt
required: all（三个路径都必须有文件）
```

**UGW 形态详细配置**：
```
路径: {网元数据文件夹}/ugw/mml
patterns:
  - omo/mml/*.txt
  - ugw/mml/mmlconf_ugw_*.txt
  - vnrs/mml/*.txt
required: all（三个路径都必须有文件）
```

---

### CloudUSN 网元详细规则

**配置**：
```
路径: omo/mml, vnrs/mml
patterns: ["*.txt"]
match_mode: any（两种目录中任意一种有文件即可）
required: true
```

---

### vCG 网元详细规则

**配置**：
```
路径: cgw/mml
patterns: ["*.txt"]
required: true（cgw/mml 目录下所有 .txt 文件都必须存在）
```

**注意**：配置待用户提供

---

### vUSN 网元详细规则

**配置**：
```
路径: - | - | - |
patterns: - | - |
required: - | - |
```

**注意**：配置待用户提供

---

### CloudSE2980 网元详细规则

**配置**：
```
路径: dataconfiguration
patterns: ["*.txt"]
match_mode: any
required: true
```

---

### SE2900 网元详细规则

**配置**：
```
路径: dataconfiguration
patterns: ["*.zip"]
match_mode: any
required: true
```

---

### CCF 网元详细规则

**配置**：
```
路径: dataconfiguration
patterns: ["*.tar.gz"]
match_mode: any
required: true
```

---

### SPSV3 网元详细规则

**配置**：
```
路径: dataconfiguration
patterns: ["*.zip"]
match_mode: any
required: true
```

---

### USC 网元详细规则

**配置**：
```
路径: dataconfiguration
patterns: ["*.tar.gz"]
match_mode: any
required: true
```

---

### HSS9860 网元详细规则

**配置**：
```
路径: dataconfiguration
patterns: ["*.tar.gz"]
match_mode: any
required: true
```

---

### UDM 网元详细规则

**配置**：
```
路径: dataconfiguration
patterns: ["*.tar.gz"]
match_mode: any
required: true
```

---

### UPCC 网元详细规则

**配置**：
```
路径: dataconfiguration
patterns: ["*.tar.gz"]
match_mode: any
required: true
```

---

### UPCF 网元详细规则

**配置**：
```
路径: dataconfiguration
patterns: ["*.tar.gz"]
match_mode: any
required: true
```

---

### ENS 网元详细规则

**配置**：
```
路径: dataconfiguration
patterns: ["*.tar.gz"]
match_mode: any
required: true
```

---

### USCDB 网元详细规则

**配置**：
```
路径: uscdb/dataconfiguration
patterns: ["*.tar.gz"]
match_mode: any
required: true
```

---

### ICG9815 网元详细规则

**配置**：
```
路径: dataconfiguration
patterns: ["*.tar.gz"]
match_mode: any
required: true
```

---

### ICG9816 网元详细规则

**配置**：
```
路径: dataconfiguration
patterns: ["*.tar.gz"]
match_mode: any
required: true
```

---

### vCG 网元详细规则

**配置**：
```
路径: - | - | - |
patterns: - | - |
required: - | - |
```

**注意**：配置待用户提供

---

### vUSN 网元详细规则

**配置**：
```
路径: - | - | - |
patterns: - | - |
required: - | - |
```

**注意**：配置待用户提供

**配置**：
```
路径: cgw/mml
patterns: ["*.txt"]
required: true（cgw/mml 目录下所有 .txt 文件都必须存在）
```

---

## 6. 文件路径构建规则

### 6.1 路径构建格式

**标准模式（any/all）**：
```
完整路径 = {网元数据文件夹}/{path}/{pattern}
示例：ATS_NE=1044_IP_10_140_2_10_59_PPR_ATS01/dataconfiguration/ALLME_ATS01.txt
```

**自定义模式（custom）**：
```
完整路径 = {网元数据文件夹}/{子目录}/{pattern}
示例：vUGW_NE=2001_IP_xxx_xxx_xxx_PPR_UGW01/ugw/mml/mmlconf_ugw_*.txt
```

### 6.2 路径构建规则

1. 路径拼接使用 `os.path.join()`，保证跨平台兼容
2. 通配符匹配使用 `glob.glob()`，`recursive=False`（只匹配一级目录）
3. 文件名匹配区分大小写
4. 路径不存在时记录为缺失

---

## 7. 校验结果结构

### 7.1 单个网元校验结果

```python
{
    'ne_name': 'ATS_NE=1044',              # 网元名称
    'ne_type': 'ATS',                    # 网元类型
    'valid': True/False,                   # 校验结果
    'missing_paths': [],                  # 缺失的文件路径列表
    'found_paths': [],                    # 找到的文件路径列表
    'deployment_mode': None,                # 部署模式（仅 vUGW）
    'description': 'Valid' 或错误信息
}
```

### 7.2 所有网元校验结果汇总

```python
{
    'total_ne_count': 5,                 # 总网元数
    'valid_ne_count': 3,                 # 校验通过的网元数
    'warning_ne_count': 1,               # 有警告的网元数
    'invalid_ne_count': 1,               # 校验失败的网元数
    'ne_results': [                      # 每个网元的详细结果
        {单个网元校验结果},
        ...
    ]
}
```

---

## 8. UI 呈现设计

### 8.1 主表格设计

保持现有结构，在 Status 列和 Details 列体现网元级状态：

```
文件名        | 路径       | 大小   | 包类型  | 状态    | 详情
nic_pkg.tar.gz | data/nic   | 2.1MB  | NIC包   | Warning  | 5/5 NEs validated, 3 have issues (click details)
```

**说明**：
- **Status** 列：如果有任何网元异常 → Warning/Invalid
- **Details** 列：汇总信息（如 "3/5 NEs have issues"）
- 点击某行 → 展开/显示详情面板

### 8.2 详情面板设计（方案2）

采用详情面板（侧边栏或底部面板）方式展示网元级详情：

```
╔═════════════════════════════════════════════════════════════════════╗
║  Package Level Issues (2)                                           ║
║    ⚠️ Collect range: 12.5h < 24h (Anonymous: true)                ║
║    ⚠️ Static MML missing for NE3 (ATS_NE=1044)                       ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  Network Element Details (5 total)                                     ║
║  ┌──────────────────────────────────────────────────────────────────────────┐   ║
║  │ [✓] NE1 (CSCF_NE=1094)                    Valid          │   ║
║  │     ✓ Folder exists                                               │   ║
║  │     ✓ Static MML: ALLME_CSCF.txt (dataconfiguration/)     │   ║
║  │     ✓ Dynamic MML exists                                        │   ║
║  │                                                                 │   ║
║  │ [⚠️] NE2 (ATS_NE=1044)                   Warning        │   ║
║  │     ✓ Folder exists                                               │   ║
║  │     ⚠️ Static MML missing                                    │   ║
║  │     Expected: dataconfiguration/*.tar.gz, *.zip, ALLME_*.txt    │   ║
║  │     Recommendation: Re-collect with static MML                │   ║
║  │                                                                 │   ║
║  │ [✓] NE3 (vUGW_NE=2001)                    Invalid         │   ║
║  │     ✓ Folder exists                                               │   ║
║  │     ⚠️ Deployment mode: ugw                                   │   ║
║  │     ✗ omo/mml/*.txt (directory not found)                     │   ║
║  │     ✓ ugw/mml/mmlconf_ugw_*.txt (2 files found)            │   ║
║  │     ✓ vnrs/mml/*.txt (5 files found)                      │   ║
║  │     ✗ Missing: ugw/mml/mmlconf_ugw_*.txt pattern         │   ║
║  │     Recommendation: Re-collect with ugw deployment          │   ║
║  │                                                                 │   ║
║  │ [✓] NE4 (CSP_NE=1095)                    Valid          │   ║
║  │     ✓ Folder exists                                               │   ║
║  │     • Static MML not required (not configured)                 │   ║
║  │                                                                 │   ║
║  │ [✓] NE5 (CGPOMU_NE=1098)                Valid          │   ║
║  │     ✓ Folder exists                                               │   ║
║  │     • Static MML not required (not configured)                 │   ║
║  └──────────────────────────────────────────────────────────────────┘   ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════╝
```

### 8.3 UI 交互设计

**交互流程**：
```
1. 扫描完成后，主表格显示所有文件
   ↓
2. 用户点击某 NIC 包行
   ↓
3. 侧边栏/底部展开详情面板
   ↓
4. 面板顶部：包级问题卡片（匿名化、时间、静态MML汇总）
   ↓
5. 面板中部：网元列表
   - 每个网元一行
   - 显示网元名称、类型、状态、详情
   - 不同状态用颜色和图标标识
   ↓
6. 用户可点击某个网元查看详细信息（如文件列表）
```

**状态颜色规范**：
| 状态 | 图标 | 颜色 | 说明 |
|------|------|------|------|
| Valid | ✓ | 绿色 #4CAF50 | 校验通过 |
| Warning | ⚠️ | 橙色 #FF9800 | 有警告（部分缺失） |
| Invalid | ✗ | 红色 #F44336 | 校验失败 |
| Not Configured | ⊘ | 灰色 #999999 | 未配置校验规则 |

---

## 9. 代码架构设计

### 9.1 文件结构

```
utils/
├── static_mml_config.yaml          # 配置文件
├── static_mml_checker.py          # 主检查器
└── custom_validators/             # 自定义校验器目录
    ├── __init__.py
    └── vUGW_validator.py          # vUGW 自定义校验器
```

### 9.2 类设计

```python
# utils/static_mml_checker.py

class StaticMMLChecker:
    """静态 MML 配置检查器"""

    def __init__(self, config_path: str):
        """初始化检查器，加载配置"""
        self.config = self._load_config(config_path)

    def check_package(self, ne_folder_path: str, ne_instances: List) -> Dict:
        """
        检查整个包的所有网元

        Args:
            ne_folder_path: 网元数据文件夹路径
            ne_instances: 网元实例列表

        Returns:
            {
                'total_ne_count': int,
                'valid_ne_count': int,
                'warning_ne_count': int,
                'invalid_ne_count': int,
                'ne_results': List[Dict]
            }
        """
        # 对每个网元进行检查
        results = []
        for ne_instance in ne_instances:
            result = self.check_ne(
                ne_folder_path,
                ne_instance.ne_type,
                ne_instance.name
            )
            results.append(result)

        # 统计结果
        return {
            'total_ne_count': len(results),
            'valid_ne_count': sum(1 for r in results if r['valid']),
            'warning_ne_count': sum(1 for r in results if r['valid'] is None),
            'invalid_ne_count': sum(1 for r in results if r['valid'] is False),
            'ne_results': results
        }

    def check_ne(self, ne_folder_path: str, ne_type: str, ne_name: str) -> Dict:
        """
        检查单个网元

        Returns:
            {
                'ne_name': str,
                'ne_type': str,
                'valid': True/False/None,
                'missing_paths': List[str],
                'found_paths': List[str],
                'deployment_mode': str or None,
                'description': str
            }
        """
        # 1. 获取该网元类型的规则
        ne_rule = self.config['static_mml_rules'].get(ne_type)

        # 2. 如果没有配置，跳过检查
        if not ne_rule:
            return {
                'ne_name': ne_name,
                'ne_type': ne_type,
                'valid': None,  # 未配置
                'missing_paths': [],
                'found_paths': [],
                'description': 'Not configured'
            }

        # 3. 检查 required 字段
        if not ne_rule.get('required', True):
            return {
                'ne_name': ne_name,
                'ne_type': ne_type,
                'valid': None,  # 不需要校验
                'missing_paths': [],
                'found_paths': [],
                'description': f'Static MML not required for {ne_type}'
            }

        # 4. 根据匹配模式调用对应的校验方法
        match_mode = ne_rule.get('match_mode', 'any')

        if match_mode == 'custom':
            return self._check_with_custom_validator(
                ne_folder_path, ne_type, ne_name, ne_rule
            )
        else:
            return self._check_with_standard_validator(
                ne_folder_path, ne_type, ne_name, ne_rule, match_mode
            )

    def _check_with_standard_validator(self, ne_folder_path: str, ne_type: str,
                                        ne_name: str, ne_rule: Dict,
                                        match_mode: str) -> Dict:
        """标准校验器（any/all）"""
        # 实现细节...

    def _check_with_custom_validator(self, ne_folder_path: str, ne_type: str,
                                        ne_name: str, ne_rule: Dict) -> Dict:
        """自定义校验器"""
        validator_name = ne_rule.get('custom_validator')

        # 动态导入自定义校验器模块
        module = importlib.import_module(f'custom_validators.{validator_name}')
        validator_func = getattr(module, 'validate_static_mml')

        # 调用自定义校验器
        return validator_func(ne_folder_path, ne_name, ne_type, ne_rule)

    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
```

```python
# utils/custom_validators/vUGW_validator.py

def validate_static_mml(ne_folder_path: str, ne_name: str, ne_type: str, config: Dict) -> Dict:
    """
    vUGW 静态 MML 校验器

    Args:
        ne_folder_path: 网元数据文件夹路径
        ne_name: 网元名称
        ne_type: 网元类型
        config: 配置信息

    Returns:
        {
            'ne_name': str,
            'ne_type': str,
            'valid': True/False,
            'missing_paths': List[str],
            'found_paths': List[str],
            'deployment_mode': str or None,
            'description': str
        }
    """
    # 定义三种部署形态及其检查路径
    deployments = {
        'cgw': {
            'paths': [
                'omo/mml/*.txt',
                'cgw/mml/mmlconf_cgw_*.txt',
                'vnrs/mml/*.txt'
            ],
            'required': 'all'
        },
        'dgw': {
            'paths': [
                'omo/mml/*.txt',
                'dgw/mml/mmlconf_dgw_*.txt',
                'vnrs/mml/*.txt'
            ],
            'required': 'all'
        },
        'ugw': {
            'paths': [
                'omo/mml/*.txt',
                'ugw/mml/mmlconf_ugw_*.txt',
                'vnrs/mml/*.txt'
            ],
            'required': 'all'
        }
    }

    # 遍历三种部署形态，找到实际存在的形态
    found_deployment = None
    missing_paths = []

    for deployment_name, deployment_config in deployments.items():
        deployment_path = os.path.join(ne_folder_path, deployment_name)

        if not os.path.exists(deployment_path):
            # 该形态的文件夹不存在，跳过
            continue

        # 检查该形态的 3 个路径
        all_missing = True
        found_any = False

        for path_pattern in deployment_config['paths']:
            # 分离路径和通配符
            parts = path_pattern.split('/')
            if len(parts) == 1:
                # 如: "omo/mml/*.txt"
                sub_dir = ''
                pattern = parts[0]
            else:
                sub_dir = parts[0]
                pattern = parts[1]

            # 构建完整路径
            if sub_dir:
                full_path = os.path.join(ne_folder_path, deployment_name, sub_dir)
            else:
                full_path = os.path.join(ne_folder_path, deployment_name)

            # 检查路径是否存在
            if not os.path.exists(full_path):
                missing_paths.append(f'{deployment_name}/{path_pattern}')
                continue

            # 查找匹配文件
            matched_files = glob.glob(os.path.join(full_path, pattern), recursive=False)

            if len(matched_files) > 0:
                # 找到文件，该路径不缺失
                all_missing = False
                found_any = True

        # 如果该形态的 3 个路径都有文件，记录为找到的形态
        if not all_missing:
            found_deployment = deployment_name
            break  # 只要有一套完整就算通过

    # 判断整体校验结果
    is_valid = found_deployment is not None

    if not is_valid:
        # 没找到任何部署形态
        if not missing_paths:
            missing_paths.append('No deployment folder found (cgw/dgw/ugw)')

    return {
        'ne_name': ne_name,
        'ne_type': ne_type,
        'valid': is_valid,
        'missing_paths': missing_paths,
        'found_paths': [],
        'deployment_mode': found_deployment,  # 仅内部使用，不呈现给用户
        'description': 'Valid' if is_valid else f'missing: {", ".join(missing_paths)}'
    }
```

---

## 10. 已知网元类型配置

### 10.1 已实现的网元类型

| 网元类型 | Match Mode | Path | Patterns | Required |
|----------|------------|------|----------|---------|
| ATS | any | dataconfiguration | *.tar.gz, *.zip, ALLME_*.txt | true |
| CSCF | any | dataconfiguration | *.tar.gz, *.zip, ALLME_*.txt | true |
| UDG | any | configuration/static | static_mml.txt | true |
| vUGW | custom | 见10.3.1 | *.txt | true（三种形态） |
| vCG | custom | 见10.3.2 | *.txt | true（三个路径） |
| vUSN | custom | 见10.3.3 | *.txt | true（四个路径） |
| CloudSE2980 | any | dataconfiguration | *.txt, *.tar.gz, *.zip | true |
| SE2900 | any | dataconfiguration | *.zip, *.txt, *.tar.gz | true |
| CCF | any | dataconfiguration | *.tar.gz | true |
| SPSV3 | any | dataconfiguration | *.zip, *.tar.gz, ALLME_*.txt | true |
| USC | any | USC/conf | *.tar.gz, *.zip, ALLME_*.txt | true |
| HSS9860 | any | dataconfiguration | *.tar.gz | true |
| UDM | any | dataconfiguration | *.tar.gz | true |
| UPCC | any | dataconfiguration | *.tar.gz | true |
| UPCF | any | dataconfiguration | *.tar.gz | true |
| ENS | any | dataconfiguration | *.tar.gz | true |
| USCDB | any | dataconfiguration | *.tar.gz | true |
| ICG9815 | any | dataconfiguration | *.tar.gz | true |
| ICG9816 | any | dataconfiguration | *.tar.gz | true |
| UNC | any | dataconfiguration | *.tar.gz | true |

| 网元类型 | Match Mode | Path | Patterns | 状态 |
|----------|------------|------|----------|------|
| ATS | any | dataconfiguration | *.tar.gz, *.zip, ALLME_*.txt | 待实现 |
| CSCF | any | dataconfiguration | *.tar.gz, *.zip, ALLME_*.txt | 待实现 |
| UDG | any | configuration/static | static_mml.txt | 待实现 |
| vUGW | custom | - | - | 待实现 |

### 10.2 不需要校验的网元类型

| 网元类型 | Required | 说明 |
|----------|----------|------|
| CSP | false | 不需要校验静态 MML |
| CGPOMU | false | 不需要校验静态 MML |

### 10.3 特殊网元类型规则

#### 10.3.1 vUGW（CNAE 内部拆分：CloudCGW / CloudDGW / CloudUGW）

**vUGW** 支持三种部署形态，满足任意一种即通过。使用 `custom` 匹配模式。

| 项目 | 配置 |
|------|------|
| **neinfo.txt 标识** | `vUGW_NE=xxx` |
| **配置文件键名** | `vUGW`（与 neinfo.txt 一致） |
| **CNAE 内部拆分** | CloudCGW, CloudDGW, CloudUGW（三种部署形态） |
| **匹配模式** | custom（自定义校验器） |
| **必需校验** | true |

**三种部署形态**（满足任意一种即通过，每种形态需要 4 个路径都存在文件）：

**形态 CGW**：
```
- omo/mml/*.txt
- vnrs/mml/*.txt
- 0/mml/*.txt
- cgw/mml/mmlconf_cgw_*.txt
```

**形态 DGW**：
```
- omo/mml/*.txt
- vnrs/mml/*.txt
- 0/mml/*.txt
- dgw/mml/mmlconf_dgw_*.txt
```

**形态 UGW**：
```
- omo/mml/*.txt
- vnrs/mml/*.txt
- 0/mml/*.txt
- ugw/mml/mmlconf_ugw_*.txt
```

**校验逻辑**：
1. 从 neinfo.txt 解析：`vUGW_NE=xxx` → 提取类型 `vUGW`
2. 使用自定义校验器 `vUGW_validator.py`
3. 依次检查三种部署形态（CGW/DGW/UGW）：
   - 每种形态需要同时存在四个路径下的 `*.txt` 文件
   - 只要找到一种完整形态，校验即通过
4. 如果三种形态都不满足，校验失败

---

#### 10.3.2 vCG（CNAE 内部叫法：CloudCG）

**vCG** 需要三个路径都存在文件。使用 `custom` 或 `all` 匹配模式。

| 项目 | 配置 |
|------|------|
| **neinfo.txt 标识** | `vCG_NE=xxx` |
| **配置文件键名** | `vCG`（与 neinfo.txt 一致） |
| **CNAE 内部叫法** | CloudCG |
| **匹配模式** | custom 或 all（需要全部满足） |
| **必需校验** | true |

**检查路径**（三个路径都要存在文件）：

```
- cg/mml/*.txt
- vnrs/mml/*.txt
- 0/mml/*.txt
```

**校验逻辑**：
1. 从 neinfo.txt 解析：`vCG_NE=xxx` → 提取类型 `vCG`
2. 查找配置中的 `vCG` 规则
3. 检查三个路径，每个路径下都必须存在至少一个 `*.txt` 文件：
   - `{网元文件夹}/cg/mml/*.txt`
   - `{网元文件夹}/vnrs/mml/*.txt`
   - `{网元文件夹}/0/mml/*.txt`
4. 只有三个路径都满足，校验才通过

---

#### 10.3.3 vUSN（CNAE 内部叫法：CloudUSN）

**vUSN** 需要四个路径都存在文件。使用 `custom` 或 `all` 匹配模式。

| 项目 | 配置 |
|------|------|
| **neinfo.txt 标识** | `vUSN_NE=xxx` |
| **配置文件键名** | `vUSN`（与 neinfo.txt 一致） |
| **CNAE 内部叫法** | CloudUSN |
| **匹配模式** | custom 或 all（需要全部满足） |
| **必需校验** | true |

**检查路径**（四个路径都要存在文件）：

```
- omo/mml/*.txt
- vnrs/mml/*.txt
- 0/mml/*.txt
- usn/mml/*.txt
```

**校验逻辑**：
1. 从 neinfo.txt 解析：`vUSN_NE=xxx` → 提取类型 `vUSN`
2. 查找配置中的 `vUSN` 规则
3. 检查四个路径，每个路径下都必须存在至少一个 `*.txt` 文件：
   - `{网元文件夹}/omo/mml/*.txt`
   - `{网元文件夹}/vnrs/mml/*.txt`
   - `{网元文件夹}/0/mml/*.txt`
   - `{网元文件夹}/usn/mml/*.txt`
4. 只有四个路径都满足，校验才通过

---

### 10.4 已核对的简单网元类型配置

#### 10.4.1 ATS

| 项目 | 配置 |
|------|------|
| **neinfo.txt 标识** | `ATS_NE=xxx` |
| **配置文件键名** | `ATS`（与 neinfo.txt 一致） |
| **匹配模式** | any（任意一个满足即可） |
| **路径** | dataconfiguration |
| **文件模式** | `*.tar.gz`, `*.zip`, `ALLME_*.txt` |
| **必需校验** | true |

**校验逻辑**：
1. 从 neinfo.txt 解析：`ATS_NE=xxx` → 提取类型 `ATS`
2. 查找配置中的 `ATS` 规则
3. 检查路径：`{网元数据文件夹}/dataconfiguration/`
4. 判断条件：该目录下只要存在以下**任意一种**文件即通过：
   - 任意 `.tar.gz` 文件
   - 任意 `.zip` 文件
   - 以 `ALLME_` 开头的 `.txt` 文件

---

#### 10.4.2 CSCF

| 项目 | 配置 |
|------|------|
| **neinfo.txt 标识** | `CSCF_NE=xxx` |
| **配置文件键名** | `CSCF`（与 neinfo.txt 一致） |
| **CNAE 内部叫法** | CSC |
| **匹配模式** | any（任意一个满足即可） |
| **路径** | dataconfiguration |
| **文件模式** | `*.tar.gz`, `*.zip`, `ALLME_*.txt` |
| **必需校验** | true |

**校验逻辑**：
1. 从 neinfo.txt 解析：`CSCF_NE=xxx` → 提取类型 `CSCF`
2. 查找配置中的 `CSCF` 规则（不是 CSC）
3. 检查路径：`{网元数据文件夹}/dataconfiguration/`
4. 判断条件：该目录下只要存在以下**任意一种**文件即通过：
   - 任意 `.tar.gz` 文件
   - 任意 `.zip` 文件
   - 以 `ALLME_` 开头的 `.txt` 文件

---

#### 10.4.3 SE2900

| 项目 | 配置 |
|------|------|
| **neinfo.txt 标识** | `SE2900_NE=xxx` |
| **配置文件键名** | `SE2900`（与 neinfo.txt 一致） |
| **匹配模式** | any（任意一个满足即可） |
| **路径** | dataconfiguration |
| **文件模式** | `*.zip`, `*.txt`, `*.tar.gz` |
| **必需校验** | true |

**校验逻辑**：
1. 从 neinfo.txt 解析出网元类型（如 `SE2900_NE=xxx`）
2. 查找配置中的 `SE2900` 规则
3. 检查路径：`{网元数据文件夹}/dataconfiguration/`
4. 判断条件：该目录下只要存在以下**任意一种**文件即通过：
   - 任意 `.zip` 文件
   - 任意 `.txt` 文件
   - 任意 `.tar.gz` 文件

---

#### 10.4.4 CloudSE2980

| 项目 | 配置 |
|------|------|
| **neinfo.txt 标识** | `CloudSE2980_NE=xxx` |
| **配置文件键名** | `CloudSE2980`（与 neinfo.txt 一致） |
| **匹配模式** | any（任意一个满足即可） |
| **路径** | dataconfiguration |
| **文件模式** | `*.txt`, `*.tar.gz`, `*.zip` |
| **必需校验** | true |

**校验逻辑**：
1. 从 neinfo.txt 解析出网元类型（如 `CloudSE2980_NE=xxx`）
2. 查找配置中的 `CloudSE2980` 规则
3. 检查路径：`{网元数据文件夹}/dataconfiguration/`
4. 判断条件：该目录下只要存在以下**任意一种**文件即通过：
   - 任意 `.txt` 文件
   - 任意 `.tar.gz` 文件
   - 任意 `.zip` 文件

---

#### 10.4.5 SPSV3（CNAE 内部叫法：SPS）

| 项目 | 配置 |
|------|------|
| **neinfo.txt 标识** | `SPSV3_NE=xxx` |
| **配置文件键名** | `SPSV3`（与 neinfo.txt 一致） |
| **CNAE 内部叫法** | SPS |
| **匹配模式** | any（任意一个满足即可） |
| **路径** | dataconfiguration |
| **文件模式** | `*.zip`, `*.tar.gz`, `ALLME_*.txt` |
| **必需校验** | true |

**校验逻辑**：
1. 从 neinfo.txt 解析：`SPSV3_NE=xxx` → 提取类型 `SPSV3`
2. 查找配置中的 `SPSV3` 规则
3. 检查路径：`{网元数据文件夹}/dataconfiguration/`
4. 判断条件：该目录下只要存在以下**任意一种**文件即通过：
   - 任意 `.zip` 文件
   - 任意 `.tar.gz` 文件
   - 以 `ALLME_` 开头的 `.txt` 文件

---

#### 10.4.6 USC

| 项目 | 配置 |
|------|------|
| **neinfo.txt 标识** | `USC_NE=xxx` |
| **配置文件键名** | `USC`（与 neinfo.txt 一致） |
| **匹配模式** | any（任意一个满足即可） |
| **路径** | USC/conf |
| **文件模式** | `*.tar.gz`, `*.zip`, `ALLME_*.txt` |
| **必需校验** | true |

**校验逻辑**：
1. 从 neinfo.txt 解析出网元类型（如 `USC_NE=xxx`）
2. 查找配置中的 `USC` 规则
3. 检查路径：`{网元数据文件夹}/USC/conf/`
4. 判断条件：该目录下只要存在以下**任意一种**文件即通过：
   - 任意 `.tar.gz` 文件
   - 任意 `.zip` 文件
   - 以 `ALLME_` 开头的 `.txt` 文件

---

## 11. 待补充的网元类型配置

所有网元类型的静态 MML 配置规则已确认完成。详见第 10 节。

### 11.1 配置填写示例

**格式说明**：
- `Path`：相对路径，相对于网元数据文件夹根目录
- `Patterns`：文件名模式列表，支持通配符 `*`
- 通配符说明：
  - `*.txt`：任意 .txt 文件
  - `ALLME_*.txt`：以 ALLME_ 开头，.txt 结尾
  - `mmlconf_ugw_*.txt`：包含 mmlconf_ugw_，后接任意字符，.txt 结尾

---

## 12. 设计决策记录

| 决策点 | 方案 A | 方案 B | 选择 | 原因 |
|---------|--------|--------|------|------|
| 配置格式 | JSON | YAML | **YAML** | 可读性更好，支持注释 |
| 校验器架构 | 单文件 | 模块化 | **模块化** | 便于扩展和维护 |
| UI 展示方式 | 表格扩展 | 详情面板 | **详情面板** | 避免表格行数爆炸 |
| 错误提示信息 | 中英双语 | 仅英文 | **英文** | 工具面向海外用户 |
| 文件名匹配 | 不区分大小写 | 区分大小写 | **区分大小写** | 避免 Unix 系统匹配问题 |

---

## 13. 实现计划

### 13.1 开发阶段

| 阶段 | 任务 | 预估 | 状态 |
|------|------|--------|------|
| 阶段1 | 配置文件编写 | 0.5h | 待完成 |
| 阶段2 | 主检查器框架搭建 | 2h | 待完成 |
| 阶段3 | vUGW 自定义校验器实现 | 1.5h | 待完成 |
| 阶段4 | 集成到现有校验流程 | 1.5h | 待完成 |
| 阶段5 | UI 详情面板实现 | 3h | 待完成 |
| 阶段6 | 测试和调试 | 2h | 待完成 |

### 13.2 待补充信息

- [ ] 所有已知网元类型的配置规则
- [ ] 其他特殊网元类型的自定义校验器（如需要）

---

**文档维护者**: Claude AI Assistant
**最后更新**: 2026-03-07
**下次更新**: 补充所有网元类型配置后
