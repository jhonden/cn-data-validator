# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Network Package Validator** - a cross-platform desktop tool for validating network data collection results (NIC/LCM/NFVI packages). It helps users identify invalid file formats, missing files, and collection issues before submitting data for assessment.

**Development Environment**: macOS/Linux
**Target Platform**: Windows/macOS/Linux
**Primary Purpose**: Validate network data packages collected from telecommunications infrastructure

---

## Essential Commands

### Running the Application

```bash
# PyQt6 GUI (recommended, primary implementation)
cd $PROJECT_ROOT
python3 src/validator_qt.py

# Command line interface (no GUI dependencies)
python3 src/validator_cli.py

# From scripts directory
scripts/run_windows/run_gui_qt.bat  # Windows
./build_macos.sh                  # macOS/Linux
```

### Building/Packaging

```bash
# Windows
scripts/run_windows/build_windows.bat

# macOS/Linux
chmod +x build_macos.sh
./build_macos.sh

# Manual packaging
cd $PROJECT_ROOT
pip install pyinstaller PyQt6
pyinstaller --onefile --windowed --name="Network Package Validator" src/validator_qt.py
```

### Testing

```bash
# Basic import test
cd $PROJECT_ROOT
python3 -c "from utils.file_scanner import FileScanner; print('OK')"

# Syntax check
python3 -m py_compile src/validator_qt.py
python3 -m py_compile src/validator_cli.py
python3 -m py_compile src/*.py
python3 -m py_compile utils/*.py

# Run specific test scripts
python3 tests/test_simple.py
python3 tests/test_nic_validation.py
python3 tests/test_scenario_validation.py

# Create test data
cd scripts/test_data_generator/
python3 create_test_nic.py
```

### Installing Dependencies

```bash
pip3 install -r requirements.txt
# Core dependencies: PyQt6, openpyxl, PyYAML
```

---

## High-Level Architecture

### Layered Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Presentation Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ validator_qt │  │validator_cli │  │ validator_psg│  │
│  │  (PyQt6)    │  │  (CLI)       │  │ (PySimpleGUI)│  │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘  │
└─────────┼──────────────────┼───────────────────────────────────┘
          │                  │
┌─────────┼──────────────────┼───────────────────────────────────┐
│         │     Business Logic Layer                            │
│  ┌──────▼──────┐  ┌────────────────────────────────┐      │
│  │FileScanner   │  │      Validation Pipeline      │      │
│  │             │  │  ┌──────────────────────┐   │      │
│  │- scan_dir() │  │  │PackageIdentifier    │   │      │
│  │- file_types │  │  │- identify()        │   │      │
│  │- validate() │  │  └──────────┬─────────┘   │      │
│  └──────────────┘  │             │               │      │
│                    │  ┌──────────▼─────────┐   │      │
│                    │  │NICValidator       │   │      │
│                    │  │- neinfo parsing   │   │      │
│                    │  │- NE folder check  │   │      │
│                    │  │- time range      │   │      │
│                    │  └──────────┬─────────┘   │      │
│                    │             │               │      │
│                    │  ┌──────────▼─────────┐   │      │
│                    │  │StaticMMLChecker   │   │      │
│                    │  │ScenarioChecker     │   │      │
│                    │  └────────────────────┘   │      │
│                    └────────────────────────────────┘      │
└────────────────────────────────────────────────────────────┘
          │
┌─────────▼───────────────────────────────────────────────────┐
│               Utility & Config Layer                        │
│  ┌──────────────────┐  ┌──────────────────────┐      │
│  │custom_validators│  │Config Files (YAML)  │      │
│  │- vUSN          │  │static_mml_config    │      │
│  │- vCG           │  │scenario_config      │      │
│  │- vUGW          │  └──────────────────────┘      │
│  │- USCDB         │                                     │
│  └──────────────────┘                                     │
└────────────────────────────────────────────────────────────┘
```

### Core Validation Pipeline

1. **File Selection** → User selects directory to scan
2. **Directory Scanning** → `FileScanner.scan_directory()` recursively walks directory
3. **File Type Validation** → Checks extension (ZIP/TAR/TAR.GZ/XLSX)
4. **Package Identification** → `PackageIdentifier.identify()` extracts and analyzes structure
5. **Deep Validation** (for NIC packages) → `NICValidator.validate()`:
   - Extract NIC package
   - Parse `neinfo.txt` (network element metadata)
   - Check collection time range from `TaskExtValue.xml`
   - Check anonymous mode setting
   - Verify NE data folders exist
   - Run NE-level static MML validation
   - Run collection scenario validation
6. **Result Display** → GUI table or CLI output
7. **Export** → TXT/CSV/Excel formats

### Key Data Flow

```
User Directory
    ↓
FileScanner (walks all files)
    ↓
For each file:
    ├─ Check extension → Valid/Invalid
    └─ If .tar.gz:
        ├─ PackageIdentifier.identify()
        │   └─ Extract to temp dir
        │       └─ Check structure
        │           └─ Match pattern: YYYYMMDDHHMMSS/ + {time}_report.tar.gz
        │               └─ Return "NIC Package"
        └─ NICValidator.validate()
            ├─ Extract NIC package
            ├─ Parse neinfo.txt → List[NEInstance]
            ├─ Check collect range (≥24h)
            ├─ Check anonymous mode (must be false)
            ├─ Check NE folders exist
            ├─ StaticMMLChecker.check_package()
            └─ ScenarioChecker.check_package()
```

---

## Important Modules

### utils/file_scanner.py

**Purpose**: Recursively scan directories and validate file formats

**Key Methods**:
- `scan_directory(progress_callback)` - Main scanning loop
- `_is_valid_file(filename)` - Check file extension
- `_validate_nic_package(nic_path, report_file_name)` - Delegate to NICValidator

**Data Structure**:
```python
{
    'path': '/full/path/to/file.tar.gz',
    'relative_path': 'subdir/file.tar.gz',
    'name': 'file.tar.gz',
    'size': 12345,
    'modified': datetime(2025, 3, 5, 10, 30, 45),
    'package_type': 'NIC Package',  # or None/Unknown
    'package_details': {...},  # From PackageIdentifier
    'nic_validation': {...}  # From NICValidator (if applicable)
}
```

### utils/package_identifier.py

**Purpose**: Identify package types by analyzing internal structure

**Supported Types**:
- `NIC Package` - Identified by time folder + report.tar.gz structure
- `LCM Package` - Not yet implemented
- `NFVI Package` - Not yet implemented
- `Unknown` - Unrecognized format

**NIC Package Pattern**:
```
nic_package.tar.gz
├── 20250203105511/              # 14-digit timestamp
│   └── ...                        # NE data folders
└── 20250203105511_report.tar.gz  # Matching report file
```

### utils/nic_validator.py

**Purpose**: Deep validation of NIC packages

**Validation Rules** (in priority order):
1. **neinfo.txt exists** - Missing = Invalid
2. **Anonymous mode** - `true` = Invalid, `false` = Valid
3. **Collection time range** - `< 24 hours` = Invalid
4. **NE types supported** - All unsupported = Invalid
5. **NE data folders** - Missing = Warning
6. **NE-level validations** - Static MML, scenarios = Warning/Info

**Supported NE Types**: UNC, UDG, vCG, vUGW, vUSN, ATS, CSCF, CloudSE2980, SE2900, CCF, SPSV3, USC, HSS9860, UDM, UPCC, UPCF, ENS, USCDB, CSP, CGPOMU

**NEInstance Class**:
```python
NEInstance(name, ne_type, instance_id, group_id, ip)
    → folder_name = "{ne_type}_{instance_id}_IP_{ip_formatted}_{group_id}_{name}"
```

### utils/static_mml_checker.py

**Purpose**: Validate NE-level static MML configurations

**Key Features**:
- Loads configuration from `static_mml_config.yaml`
- Supports multiple match modes: EXACT, CONTAINS, REGEX
- Custom validators per NE type (vCG, vUGW, vUSN, USCDB)

### utils/scenario_checker.py

**Purpose**: Validate network element collection scenarios

**Key Features**:
- Loads configuration from `scenario_config.yaml`
- Checks if NE supports required scenarios
- Validates scenario parameter formats (dotted notation)

---

## Critical Constraints

### Technical Stack (MUST FOLLOW)

| Component | Required Technology |
|-----------|---------------------|
| GUI Framework | **PyQt6** (primary), CustomTkinter (backup) |
| Language | Python 3.9+ |
| Packaging | PyInstaller |
| File Processing | tarfile, zipfile |

### Language Requirements

**GUI Interface Text: MUST be in English**
- Buttons, labels, tooltips, error messages
- Table headers
- Status messages

**Code Comments and Docs: Use Chinese**
- Code comments
- Docstrings
- Documentation files

**Exception**: CLI interface (`validator_cli.py`) may use Chinese for domestic users.

### Windows Deployment Requirements

**CRITICAL for .bat files:**
- **MUST use CRLF line endings** (`\r\n`)
- After editing .bat files, run: `unix2dos build_windows.bat` or `sed -i '' 's/$/\r/' build_windows.bat`
- **MUST set encoding**: Add `set PYTHONIOENCODING=utf-8` at the top

**Python Files:**
- **MUST include encoding declaration**: `# -*- coding: utf-8 -*-` at the top
- Use LF line endings (Unix-style, Git default)

### Project Root Directory

**When running commands, ensure working directory is project root:**

```bash
# Get project root dynamically
export PROJECT_ROOT=$(git rev-parse --show-toplevel)
cd $PROJECT_ROOT
python3 src/validator_qt.py
```

---

## Configuration Files

### utils/static_mml_config.yaml

Defines static MML validation rules for different NE types.

**Structure**:
```yaml
vCG:
  rules:
    - name: "example rule"
      patterns: ["pattern1", "pattern2"]
      match_mode: "EXACT|CONTAINS|REGEX"
      expected_values: ["value1"]
```

### utils/scenario_config.yaml

Defines collection scenario requirements for different NE types.

---

## Common Patterns

### Adding New Package Type Support

1. Add type constant to `PackageIdentifier` class
2. Implement `_identify_xxx_package()` method
3. Add corresponding validator class (e.g., `LCMValidator`)
4. Update `FileScanner._validate_xxx_package()` to call new validator
5. Add config YAML file if needed

### Adding New NE Type Validation

1. Add NE type to `NICValidator.SUPPORTED_NE_TYPES`
2. Add required files to `NICValidator.NE_REQUIRED_FILES` (if applicable)
3. Create custom validator in `utils/custom_validators/{type}_validator.py`
4. Add configuration to `static_mml_config.yaml` or `scenario_config.yaml`

### Adding Custom Validation Rules

1. Define rule in config YAML
2. Implement in appropriate checker class (`StaticMMLChecker` or `ScenarioChecker`)
3. Return result in standard format with `valid`, `errors`, `warnings`

---

## Validation Error Priority

Display errors in this order (highest to lowest):
1. Missing neinfo.txt (Invalid - red)
2. Anonymous collection mode (Invalid - red)
3. Collection time range < 24h (Invalid - red)
4. All NE types unsupported (Invalid - red)
5. Missing NE data folders (Warning - orange)
6. Missing key files (Warning - orange)
7. Static MML issues (Warning/info)
8. Scenario issues (Warning/info)

---

## Testing Strategy

### Unit Test Scripts
- `test_simple.py` - Basic import and dependency tests
- `test_nic_validation.py` - NIC package validation tests
- `test_scenario_validation.py` - Scenario validation tests
- `test_modules.py` - Core module tests

### Test Data Location
- `tests/data/test_data/` - Contains sample NIC packages for testing
- `tests/data/test_packages/` - Additional test packages

### Creating Test NIC Packages
- `tests/data/test_data_generator/` - Test data generation scripts
  - `create_nic_package.py` - Create standard test package
  - `create_anonymous_nic.py` - Create anonymous mode package (should fail)
- `create_short_collect_range_nic.py` - Create <24h collection package (should fail)
- `create_unsupported_nic.py` - Create package with all unsupported NE types (should fail)

---

## Design Tokens (GUI)

Located in `utils/design_tokens.py` and `utils/typography.py`

**Colors**:
- Valid status: `#4CAF50` (green)
- Invalid status: `#F44336` (red)
- Warning status: `#FF9800` (orange)
- NIC Package: `#2196F3` (blue)
- Unknown Package: `#FF9800` (orange)

**Usage** (PyQt6):
```python
from utils.design_tokens import COLORS
cell.setBackground(QColor(COLORS['valid']))
```

---

## Resource Path Handling

**For PyInstaller compatibility**:

```python
def get_resource_path(relative_path: str) -> str:
    """Get absolute path to resource file, works in dev and packaged environment"""
    try:
        # PyInstaller temp folder
        base_path = sys._MEIPASS
        return os.path.join(base_path, 'utils', os.path.basename(relative_path))
    except AttributeError:
        # Development environment
        return os.path.join(os.path.dirname(__file__), relative_path)
```

Use this when loading YAML configs or other bundled resources.

---

## Git Workflow

### Commit Standards

**After modifying code, you MUST verify before committing:**

```bash
# 1. Compile check
python3 -m py_compile src/validator_qt.py
python3 -m py_compile utils/*.py

# 2. Import test
python3 -c "from validator_qt import ValidatorApp; print('OK')"

# 3. Run the app
python3 src/validator_qt.py

# 4. Ask user for confirmation before committing
```

**Commit message format** (Chinese):
```bash
git commit -m "feat: 添加 NIC 包识别功能"
git commit -m "fix: 修复中文编码问题"
git commit -m "docs: 更新开发规范文档"
```

**Types**: feat, fix, refactor, docs, test, perf, style

### Verification Checklist

Before committing:
- [ ] Python compiles successfully
- [ ] Program starts without errors
- [ ] GUI displays correctly
- [ ] Basic functionality works
- [ ] User confirms commit is OK

---

## Development Standards Location

All project standards are documented in `docs/standards/`:

- `development-conventions.md` - Coding standards, file format rules, line ending requirements
- `code-submission-workflow.md` - Verification and commit workflow
- `project-constraints.md` - Technology stack, functional scope, performance constraints

**READ THESE before making changes.**

---

## Known Issues

1. **macOS Tkinter Compatibility**: CustomTkinter version fails on certain macOS versions. Use PyQt6 version instead.

2. **PyInstaller Bundle Size**: PyQt6 bundles are large (50-100MB). This is expected.

3. **Windows Encoding**: .bat files MUST use CRLF line endings and set `PYTHONIOENCODING=utf-8`.

---

## Future Enhancements

**High Priority**:
- LCM package recognition rules
- NFVI package recognition rules
- Extended NIC package validation (additional file types)

**Medium Priority**:
- Package dependency checking (e.g., CloudSE2980 → ENS PGW)
- Multi-package combination validation rules

**Low Priority**:
- Config file support for validation rules
- Batch rule import/export
- Table sorting and filtering features
