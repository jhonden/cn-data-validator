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
  # 网元类型配置（详细规则见第 9 节）

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

## 5. 文件路径构建规则

### 5.1 路径构建格式

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

### 5.2 路径构建规则

1. 路径拼接使用 `os.path.join()`，保证跨平台兼容
2. 通配符匹配使用 `glob.glob()`，`recursive=False`（只匹配一级目录）
3. 文件名匹配区分大小写
4. 路径不存在时记录为缺失

---

## 6. 校验结果结构

### 6.1 单个网元校验结果

```python
{
    'ne_name': str,
    'ne_type': str,
    'valid': True/False/None,
    'missing_paths': List[str],
    'found_paths': List[str],
    'deployment_mode': str or None,
    'description': str
}
```

**字段说明**：
- `valid`: True（通过）/ False（失败）/ None（未配置或不需要校验）
- `missing_paths`: 缺失的文件路径列表
- `found_paths`: 找到的文件路径列表
- `deployment_mode`: 部署模式（仅 vUGW 等特殊网元使用，内部使用）
- `description`: 描述信息，用于 UI 显示

### 6.2 所有网元校验结果汇总

```python
{
    'total_ne_count': int,
    'valid_ne_count': int,
    'warning_ne_count': int,
    'invalid_ne_count': int,
    'ne_results': List[Dict]
}
```

---

## 7. UI 呈现设计

### 7.1 主表格设计

保持现有结构，在 Status 列和 Details 列体现网元级状态：

```
文件名        | 路径       | 大小   | 包类型  | 状态    | 详情
nic_pkg.tar.gz | data/nic   | 2.1MB  | NIC包   | Warning  | 5/5 NEs validated, 3 have issues (click details)
```

**说明**：
- **Status** 列：如果有任何网元异常 → Warning/Invalid
- **Details** 列：汇总信息（如 "3/5 NEs have issues"）
- 点击某行 → 展开/显示详情面板

### 7.2 详情面板设计（方案2）

采用详情面板（侧边栏或底部面板）方式展示网元级详情：

```
╔═══════════════════════════════════════════════════════════════════╗
║  Package Level Issues (2)                                           ║
║    ⚠️ Collect range: 12.5h < 24h (Anonymous: true)                ║
║    ⚠️ Static MML missing for NE3 (ATS_NE=1044)                       ║
╠════════════════════════════════════════════════════════════════╣
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
║  └──────────────────────────────────────────────────────────────────────────┘   ║
╚═════════════════════════════════════════════════════════════════════╝
```

### 7.3 UI 交互设计

**交互流程**：
1. 用户点击表格中的 NIC 包行
2. 右侧/底部弹出详情面板
3. 面板顶部显示包级别问题（如果有）
4. 面板中部显示网元列表，每个网元展开显示详细信息
5. 用户可以收起/展开各个网元

**视觉反馈**：
- ✓ 绿色：校验通过
- ⚠️ 黄色：警告（缺少部分文件）
- ✗ 红色：失败（缺少关键配置）
- 路径缺失：显示为 `✗ path (missing)`

---

## 8. 代码架构设计

### 8.1 文件结构

```
utils/
├── static_mml_config.yaml          # 配置文件
├── static_mml_checker.py          # 主检查器
└── custom_validators/             # 自定义校验器目录
    ├── __init__.py
    └── vUGW_validator.py          # vUGW 自定义校验器
```

### 8.2 类设计

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
                'vnrs/mml/*.txt',
                '0/mml/*.txt'
            ],
            'required': 'all'
        },
        'dgw': {
            'paths': [
                'omo/mml/*.txt',
                'dgw/mml/mmlconf_dgw_*.txt',
                'vnrs/mml/*.txt',
                '0/mml/*.txt'
            ],
            'required': 'all'
        },
        'ugw': {
            'paths': [
                'omo/mml/*.txt',
                'ugw/mml/mmlconf_ugw_*.txt',
                'vnrs/mml/*.txt',
                '0/mml/*.txt'
            ],
            'required': 'all'
        }
    }

    missing_paths = []
    found_deployment = None
    found_any = False

    # 依次检查三种部署形态
    for deployment_name, deployment in deployments.items():
        deployment_complete = True

        for path_pattern in deployment['paths']:
            full_path = os.path.join(ne_folder_path, path_pattern.replace('*.txt', ''))
            glob_pattern = os.path.join(ne_folder_path, path_pattern)

            # 使用 glob 查找文件
            files = glob.glob(glob_pattern)

            if files:
                found_any = True
            else:
                deployment_complete = False
                missing_paths.append(path_pattern)

        # 如果该形态的 4 个路径都有文件，记录为找到的形态
        if deployment_complete:
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

## 9. 网元类型静态 MML 校验规则

本节详细记录所有网元类型的静态 MML 校验规则，每种网元类型一个独立小节。

### 9.1 特殊网元类型

#### 9.1.1 vUGW（CNAE 内部拆分：CloudCGW / CloudDGW / CloudUGW）

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

**数据示例**：
```
网元文件夹: vUGW_NE=2001_IP_10_140_2_20_100_PPR_UGW01
有效形态 CGW:
  - vUGW_NE=2001_IP_10_140_2_20_100_PPR_UGW01/omo/mml/omo_config.txt
  - vUGW_NE=2001_IP_10_140_2_20_100_PPR_UGW01/vnrs/mml/vnrs_config.txt
  - vUGW_NE=2001_IP_10_140_2_20_100_PPR_UGW01/0/mml/0_config.txt
  - vUGW_NE=2001_IP_10_140_2_20_100_PPR_UGW01/cgw/mml/mmlconf_cgw_001.txt
```

---

#### 9.1.2 vCG（CNAE 内部叫法：CloudCG）

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

**数据示例**：
```
网元文件夹: vCG_NE=3001_IP_10_140_2_30_100_PPR_CG01
有效路径:
  - vCG_NE=3001_IP_10_140_2_30_100_PPR_CG01/cg/mml/cg_config.txt
  - vCG_NE=3001_IP_10_140_2_30_100_PPR_CG01/vnrs/mml/vnrs_config.txt
  - vCG_NE=3001_IP_10_140_2_30_100_PPR_CG01/0/mml/0_config.txt
```

---

#### 9.1.3 vUSN（CNAE 内部叫法：CloudUSN）

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

**数据示例**：
```
网元文件夹: vUSN_NE=4001_IP_10_140_2_40_100_PPR_USN01
有效路径:
  - vUSN_NE=4001_IP_10_140_2_40_100_PPR_USN01/omo/mml/omo_config.txt
  - vUSN_NE=4001_IP_10_140_2_40_100_PPR_USN01/vnrs/mml/vnrs_config.txt
  - vUSN_NE=4001_IP_10_140_2_40_100_PPR_USN01/0/mml/0_config.txt
  - vUSN_NE=4001_IP_10_140_2_40_100_PPR_USN01/usn/mml/usn_config.txt
```

---

### 9.2 已核对的简单网元类型

#### 9.2.1 ATS

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

**数据示例**：
```
网元文件夹: ATS_NE=1044_IP_10_140_2_10_59_PPR_ATS01
有效文件:
  - ATS_NE=1044_IP_10_140_2_10_59_PPR_ATS01/dataconfiguration/ALLME_ATS01.txt
  或
  - ATS_NE=1044_IP_10_140_2_10_59_PPR_ATS01/dataconfiguration/data.tar.gz
  或
  - ATS_NE=1044_IP_10_140_2_10_59_PPR_ATS01/dataconfiguration/data.zip
```

---

#### 9.2.2 CSCF

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

**数据示例**：
```
网元文件夹: CSCF_NE=1094_IP_10_140_2_1_56_PPR_CSCF01
有效文件:
  - CSCF_NE=1094_IP_10_140_2_1_56_PPR_CSCF01/dataconfiguration/ALLME_CSCF01.txt
```

---

#### 9.2.3 SE2900

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

**数据示例**：
```
网元文件夹: SE2900_NE=5001_IP_10_140_2_50_100_PPR_SE290001
有效文件:
  - SE2900_NE=5001_IP_10_140_2_50_100_PPR_SE290001/dataconfiguration/data.zip
  或
  - SE2900_NE=5001_IP_10_140_2_50_100_PPR_SE290001/dataconfiguration/config.txt
```

---

#### 9.2.4 CloudSE2980

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

**数据示例**：
```
网元文件夹: CloudSE2980_NE=6001_IP_10_140_2_60_100_PPR_SE298001
有效文件:
  - CloudSE2980_NE=6001_IP_10_140_2_60_100_PPR_SE298001/dataconfiguration/config.txt
```

---

#### 9.2.5 SPSV3（CNAE 内部叫法：SPS）

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

**数据示例**：
```
网元文件夹: SPSV3_NE=7001_IP_10_140_2_70_100_PPR_SPSV301
有效文件:
  - SPSV3_NE=7001_IP_10_140_2_70_100_PPR_SPSV301/dataconfiguration/data.zip
```

---

#### 9.2.6 USC

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

**数据示例**：
```
网元文件夹: USC_NE=8001_IP_10_140_2_80_100_PPR_USC01
有效文件:
  - USC_NE=8001_IP_10_140_2_80_100_PPR_USC01/USC/conf/ALLME_USC01.txt
```

---

### 9.3 待核对的网元类型

以下网元类型的校验规则尚未与用户核对，配置信息仅供参考。

#### 9.3.1 UDG

| 项目 | 配置（待核对） |
|------|------|
| **neinfo.txt 标识** | `UDG_NE=xxx` |
| **配置文件键名** | `UDG`（与 neinfo.txt 一致） |
| **匹配模式** | any（任意一个满足即可） |
| **路径** | configuration/static |
| **文件模式** | `static_mml.txt` |
| **必需校验** | true |

**校验逻辑**：
1. 从 neinfo.txt 解析出网元类型（如 `UDG_NE=xxx`）
2. 查找配置中的 `UDG` 规则
3. 检查路径：`{网元数据文件夹}/configuration/static/`
4. 判断条件：该目录下只要存在 `static_mml.txt` 文件即通过

---

#### 9.3.2 CCF

| 项目 | 配置（待核对） |
|------|------|
| **neinfo.txt 标识** | `CCF_NE=xxx` |
| **配置文件键名** | `CCF`（与 neinfo.txt 一致） |
| **匹配模式** | any（任意一个满足即可） |
| **路径** | dataconfiguration |
| **文件模式** | `*.tar.gz` |
| **必需校验** | true |

**校验逻辑**：
1. 从 neinfo.txt 解析出网元类型（如 `CCF_NE=xxx`）
2. 查找配置中的 `CCF` 规则
3. 检查路径：`{网元数据文件夹}/dataconfiguration/`
4. 判断条件：该目录下只要存在任意一个 `.tar.gz` 文件即通过

---

#### 9.3.3 HSS9860

| 项目 | 配置（待核对） |
|------|------|
| **neinfo.txt 标识** | `HSS9860_NE=xxx` |
| **配置文件键名** | `HSS9860`（与 neinfo.txt 一致） |
| **匹配模式** | any（任意一个满足即可） |
| **路径** | dataconfiguration |
| **文件模式** | `*.tar.gz` |
| **必需校验** | true |

**校验逻辑**：
1. 从 neinfo.txt 解析出网元类型（如 `HSS9860_NE=xxx`）
2. 查找配置中的 `HSS9860` 规则
3. 检查路径：`{网元数据文件夹}/dataconfiguration/`
4. 判断条件：该目录下只要存在任意一个 `.tar.gz` 文件即通过

---

#### 9.3.4 UDM

| 项目 | 配置（待核对） |
|------|------|
| **neinfo.txt 标识** | `UDM_NE=xxx` |
| **配置文件键名** | `UDM`（与 neinfo.txt 一致） |
| **匹配模式** | any（任意一个满足即可） |
| **路径** | dataconfiguration |
| **文件模式** | `*.tar.gz` |
| **必需校验** | true |

**校验逻辑**：
1. 从 neinfo.txt 解析出网元类型（如 `UDM_NE=xxx`）
2. 查找配置中的 `UDM` 规则
3. 检查路径：`{网元数据文件夹}/dataconfiguration/`
4. 判断条件：该目录下只要存在任意一个 `.tar.gz` 文件即通过

---

#### 9.3.5 UPCC

| 项目 | 配置（待核对） |
|------|------|
| **neinfo.txt 标识** | `UPCC_NE=xxx` |
| **配置文件键名** | `UPCC`（与 neinfo.txt 一致） |
| **匹配模式** | any（任意一个满足即可） |
| **路径** | dataconfiguration |
| **文件模式** | `*.tar.gz` |
| **必需校验** | true |

**校验逻辑**：
1. 从 neinfo.txt 解析出网元类型（如 `UPCC_NE=xxx`）
2. 查找配置中的 `UPCC` 规则
3. 检查路径：`{网元数据文件夹}/dataconfiguration/`
4. 判断条件：该目录下只要存在任意一个 `.tar.gz` 文件即通过

---

#### 9.3.6 UPCF

| 项目 | 配置（待核对） |
|------|------|
| **neinfo.txt 标识** | `UPCF_NE=xxx` |
| **配置文件键名** | `UPCF`（与 neinfo.txt 一致） |
| **匹配模式** | any（任意一个满足即可） |
| **路径** | dataconfiguration |
| **文件模式** | `*.tar.gz` |
| **必需校验** | true |

**校验逻辑**：
1. 从 neinfo.txt 解析出网元类型（如 `UPCF_NE=xxx`）
2. 查找配置中的 `UPCF` 规则
3. 检查路径：`{网元数据文件夹}/dataconfiguration/`
4. 判断条件：该目录下只要存在任意一个 `.tar.gz` 文件即通过

---

#### 9.3.7 ENS

| 项目 | 配置（待核对） |
|------|------|
| **neinfo.txt 标识** | `ENS_NE=xxx` |
| **配置文件键名** | `ENS`（与 neinfo.txt 一致） |
| **匹配模式** | any（任意一个满足即可） |
| **路径** | dataconfiguration |
| **文件模式** | `*.tar.gz` |
| **必需校验** | true |

**校验逻辑**：
1. 从 neinfo.txt 解析出网元类型（如 `ENS_NE=xxx`）
2. 查找配置中的 `ENS` 规则
3. 检查路径：`{网元数据文件夹}/dataconfiguration/`
4. 判断条件：该目录下只要存在任意一个 `.tar.gz` 文件即通过

---

#### 9.3.8 USCDB

| 项目 | 配置（待核对） |
|------|------|
| **neinfo.txt 标识** | `USCDB_NE=xxx` |
| **配置文件键名** | `USCDB`（与 neinfo.txt 一致） |
| **匹配模式** | any（任意一个满足即可） |
| **路径** | dataconfiguration |
| **文件模式** | `*.tar.gz` |
| **必需校验** | true |

**校验逻辑**：
1. 从 neinfo.txt 解析出网元类型（如 `USCDB_NE=xxx`）
2. 查找配置中的 `USCDB` 规则
3. 检查路径：`{网元数据文件夹}/dataconfiguration/`
4. 判断条件：该目录下只要存在任意一个 `.tar.gz` 文件即通过

---

#### 9.3.9 ICG9815

| 项目 | 配置（待核对） |
|------|------|
| **neinfo.txt 标识** | `ICG9815_NE=xxx` |
| **配置文件键名** | `ICG9815`（与 neinfo.txt 一致） |
| **匹配模式** | any（任意一个满足即可） |
| **路径** | dataconfiguration |
| **文件模式** | `*.tar.gz` |
| **必需校验** | true |

**校验逻辑**：
1. 从 neinfo.txt 解析出网元类型（如 `ICG9815_NE=xxx`）
2. 查找配置中的 `ICG9815` 规则
3. 检查路径：`{网元数据文件夹}/dataconfiguration/`
4. 判断条件：该目录下只要存在任意一个 `.tar.gz` 文件即通过

---

#### 9.3.10 ICG9816

| 项目 | 配置（待核对） |
|------|------|
| **neinfo.txt 标识** | `ICG9816_NE=xxx` |
| **配置文件键名** | `ICG9816`（与 neinfo.txt 一致） |
| **匹配模式** | any（任意一个满足即可） |
| **路径** | dataconfiguration |
| **文件模式** | `*.tar.gz` |
| **必需校验** | true |

**校验逻辑**：
1. 从 neinfo.txt 解析出网元类型（如 `ICG9816_NE=xxx`）
2. 查找配置中的 `ICG9816` 规则
3. 检查路径：`{网元数据文件夹}/dataconfiguration/`
4. 判断条件：该目录下只要存在任意一个 `.tar.gz` 文件即通过

---

#### 9.3.11 UNC

| 项目 | 配置（待核对） |
|------|------|
| **neinfo.txt 标识** | `UNC_NE=xxx` |
| **配置文件键名** | `UNC`（与 neinfo.txt 一致） |
| **匹配模式** | any（任意一个满足即可） |
| **路径** | dataconfiguration |
| **文件模式** | `*.tar.gz` |
| **必需校验** | true |

**校验逻辑**：
1. 从 neinfo.txt 解析出网元类型（如 `UNC_NE=xxx`）
2. 查找配置中的 `UNC` 规则
3. 检查路径：`{网元数据文件夹}/dataconfiguration/`
4. 判断条件：该目录下只要存在任意一个 `.tar.gz` 文件即通过

---

### 9.4 不需要校验的网元类型

| 网元类型 | Required | 说明 |
|----------|----------|------|
| CSP | false | 不需要校验静态 MML |
| CGPOMU | false | 不需要校验静态 MML |

---

## 10. 配置填写示例

### 10.1 配置格式说明

**格式说明**：
- `Path`：相对路径，相对于网元数据文件夹根目录
- `Patterns`：文件名模式列表，支持通配符 `*`
- 通配符说明：
  - `*.txt`：任意 .txt 文件
  - `ALLME_*.txt`：以 ALLME_ 开头，.txt 结尾
  - `mmlconf_ugw_*.txt`：包含 mmlconf_ugw_，后接任意字符，.txt 结尾

---

## 11. 设计决策记录

| 决策点 | 方案 A | 方案 B | 选择 | 原因 |
|---------|--------|--------|------|------|
| 配置格式 | JSON | YAML | **YAML** | 可读性更好，支持注释 |
| 校验器架构 | 单文件 | 模块化 | **模块化** | 便于扩展和维护 |
| UI 展示方式 | 表格扩展 | 详情面板 | **详情面板** | 避免表格行数爆炸 |
| 错误提示信息 | 中英双语 | 仅英文 | **英文** | 工具面向海外用户 |
| 文件名匹配 | 不区分大小写 | 区分大小写 | **区分大小写** | 避免 Unix 系统匹配问题 |

---

## 12. 实现计划

### 12.1 开发阶段

| 阶段 | 任务 | 预估 | 状态 |
|------|------|--------|------|
| 阶段1 | 配置文件编写 | 0.5h | 待完成 |
| 阶段2 | 主检查器框架搭建 | 2h | 待完成 |
| 阶段3 | vUGW 自定义校验器实现 | 1.5h | 待完成 |
| 阶段4 | 集成到现有校验流程 | 1.5h | 待完成 |
| 阶段5 | UI 详情面板实现 | 3h | 待完成 |
| 阶段6 | 测试和调试 | 2h | 待完成 |

### 12.2 待补充信息

- [ ] 待核对网元类型的校验规则：UDG, CCF, HSS9860, UDM, UPCC, UPCF, ENS, USCDB, ICG9815, ICG9816, UNC
- [ ] 其他特殊网元类型的自定义校验器（如需要）

---

**文档维护者**: Claude AI Assistant
**最后更新**: 2026-03-07
**下次更新**: 补充所有网元类型配置后
