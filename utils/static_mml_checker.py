"""
Static MML Configuration Checker
网元级别静态 MML 配置检查器

Supports three match modes:
- any: Any pattern match passes
- all: All patterns must match
- custom: Use custom validator function
"""

import os
import glob
import importlib
from typing import Dict, List, Optional
import yaml


class StaticMMLChecker:
    """Static MML Configuration Checker"""

    def __init__(self, config_path: str, scenario_config_path: Optional[str] = None):
        """
        Initialize checker and load configuration

        Args:
            config_path: Path to configuration file (static_mml_config.yaml)
            scenario_config_path: Path to scenario configuration file (scenario_config.yaml)
        """
        self.config_path = config_path
        self.config = self._load_config()

        # Load scenario configuration
        if scenario_config_path:
            self.scenario_config = self._load_scenario_config(scenario_config_path)
        else:
            self.scenario_config = None

    def _load_config(self) -> Dict:
        """Load configuration file"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _load_scenario_config(self, scenario_path: str) -> Dict:
        """Load scenario configuration file"""
        with open(scenario_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def check_package(self, ne_parent_path: str, ne_instances: List) -> Dict:
        """
        Check all NEs in a package

        Args:
            ne_parent_path: NE data parent folder path (containing all NE folders)
            ne_instances: List of NEInstance objects

        Returns:
            {
                'total_ne_count': int,
                'valid_ne_count': int,
                'warning_ne_count': int,
                'invalid_ne_count': int,
                'ne_results': List[Dict]
            }
        """
        # Check collection scenario first
        scenario_errors = []
        scenario_error_count = 0

        # Check each NE
        results = []
        for ne_instance in ne_instances:
            # Build full NE folder path
            ne_folder_path = os.path.join(ne_parent_path, ne_instance.folder_name)
            result = self.check_ne(
                ne_folder_path,
                ne_instance.ne_type,
                ne_instance.name
            )

            # Check for collection scenario errors
            scenario_result = self._check_collection_scenario(
                ne_parent_path,
                ne_instance.ne_type,
                ne_instance.name
            )
            if scenario_result:
                result['valid'] = False
                result['scenario_error'] = scenario_result
                scenario_error_count += 1
                scenario_errors.append({
                    'ne_name': ne_instance.name,
                    'ne_type': ne_instance.ne_type,
                    'error': scenario_result
                })

            results.append(result)

        # Aggregate results
        return {
            'total_ne_count': len(results),
            'valid_ne_count': sum(1 for r in results if r['valid'] is True),
            'warning_ne_count': sum(1 for r in results if r['valid'] is None),
            'invalid_ne_count': sum(1 for r in results if r['valid'] is False),
            'ne_results': results,
            'scenario_error_count': scenario_error_count,
            'scenario_errors': scenario_errors if scenario_error_count > 0 else []
        }

    def _check_collection_scenario(self, ne_parent_path: str, ne_type: str, ne_name: str) -> Optional[str]:
        """
        Check collection scenario by reading taskinfo.txt

        Args:
            ne_parent_path: NE data parent folder path
            ne_type: NE type
            ne_name: NE instance name

        Returns:
            Error message if scenario mismatch, None otherwise
        """
        if not self.scenario_config:
            return None

        # Read taskinfo.txt to get scenario
        taskinfo_path = os.path.join(ne_parent_path, 'taskinfo.txt')
        if not os.path.exists(taskinfo_path):
            return None

        try:
            with open(taskinfo_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('scenario_group_name='):
                        # Extract scenario name after '=' and before ';'
                        scenario_part = line.split('=')[1].split(';')[0]
                        return self._format_scenario_error(ne_type, ne_name, scenario_part)
        except Exception as e:
            return self._format_scenario_error(ne_type, ne_name, f"Error reading taskinfo.txt: {str(e)}")

    def _format_scenario_error(self, ne_type: str, ne_name: str, actual_scenario: str) -> str:
        """
        Format scenario error message with language support

        Args:
            ne_type: NE type
            ne_name: NE instance name
            actual_scenario: Actual scenario name from taskinfo.txt

        Returns:
            Formatted error message
        """
        # Get language from config (default to English)
        ui_language = self.scenario_config.get('ui_language', 'en')

        # Get expected scenario for this NE type
        expected_scenario_info = self.scenario_config.get('scenarios', {}).get(ne_type, {})
        expected_scenario = expected_scenario_info.get('en', '')

        if not expected_scenario:
            return None

        # Compare and format error message
        if actual_scenario != expected_scenario:
            if ui_language == 'zh':
                return f"网元采集场景错误：网元'{ne_name}'（{ne_type}）应该使用'{expected_scenario}'采集场景"
            else:
                return f"Collection scenario error: NE '{ne_name}' ({ne_type}) should use '{expected_scenario}' collection scenario"

        return None

    def check_ne(self, ne_folder_path: str, ne_type: str, ne_name: str) -> Dict:
        """
        Check a single NE

        Args:
            ne_folder_path: Full NE data folder path (e.g., /path/ATS_NE=1_IP_10_140_1_1_PPR_ATS01)
            ne_type: NE type (e.g., ATS, CSCF, vUGW)
            ne_name: NE instance name

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
        # Get rule for this NE type
        ne_rule = self.config.get('static_mml_rules', {}).get(ne_type)

        # If not configured, skip check
        if not ne_rule:
            return {
                'ne_name': ne_name,
                'ne_type': ne_type,
                'valid': None,  # Not configured
                'missing_paths': [],
                'found_paths': [],
                'deployment_mode': None,
                'description': 'Not configured'
            }

        # Check required field
        if not ne_rule.get('required', True):
            return {
                'ne_name': ne_name,
                'ne_type': ne_type,
                'valid': None,  # Not required
                'missing_paths': [],
                'found_paths': [],
                'deployment_mode': None,
                'description': ne_rule.get('description', f'Static MML not required for {ne_type}')
            }

        # Call appropriate validator based on match mode
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
        """
        Standard validator for any/all match modes

        Args:
            ne_folder_path: NE data folder path
            ne_type: NE type
            ne_name: NE instance name
            ne_rule: NE rule configuration
            match_mode: 'any' or 'all'

        Returns:
            Validation result dictionary
        """
        path = ne_rule.get('path', '')
        patterns = ne_rule.get('patterns', [])
        description = ne_rule.get('description', 'Static MML Configuration')

        # Build full search path
        search_path = os.path.join(ne_folder_path, path)

        # Check if path exists
        if not os.path.exists(search_path):
            # Format missing paths list
            missing = [f"{path}/{p}" for p in patterns] if path else patterns
            return {
                'ne_name': ne_name,
                'ne_type': ne_type,
                'valid': False,
                'missing_paths': missing,
                'found_paths': [],
                'deployment_mode': None,
                'description': f'Directory not found: {path}'
            }

        # Check each pattern
        found_files = []
        missing_patterns = []

        for pattern in patterns:
            glob_pattern = os.path.join(search_path, pattern)
            matched_files = glob.glob(glob_pattern)

            if matched_files:
                found_files.extend(matched_files)
            else:
                missing_patterns.append(f"{path}/{pattern}")

        # Determine result based on match mode
        if match_mode == 'any':
            # Any match passes
            is_valid = len(found_files) > 0
            result_desc = description if is_valid else f'missing: {", ".join(missing_patterns)}'
        else:  # match_mode == 'all'
            # All patterns must match
            is_valid = len(missing_patterns) == 0
            result_desc = description if is_valid else f'missing: {", ".join(missing_patterns)}'

        return {
            'ne_name': ne_name,
            'ne_type': ne_type,
            'valid': is_valid,
            'missing_paths': missing_patterns if not is_valid else [],
            'found_paths': found_files,
            'deployment_mode': None,
            'description': result_desc
        }

    def _check_with_custom_validator(self, ne_folder_path: str, ne_type: str,
                                     ne_name: str, ne_rule: Dict) -> Dict:
        """
        Custom validator for special NE types

        Args:
            ne_folder_path: NE data folder path
            ne_type: NE type
            ne_name: NE instance name
            ne_rule: NE rule configuration

        Returns:
            Validation result dictionary from custom validator
        """
        validator_name = ne_rule.get('custom_validator')
        if not validator_name:
            return {
                'ne_name': ne_name,
                'ne_type': ne_type,
                'valid': False,
                'missing_paths': [],
                'found_paths': [],
                'deployment_mode': None,
                'description': 'Custom validator not specified'
            }

        try:
            # Dynamically import custom validator module
            # Add current directory to path to ensure we can import from utils.custom_validators
            import sys
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)

            module_path = importlib.import_module(f'custom_validators.{validator_name}')
            validator_func = getattr(module_path, 'validate_static_mml')

            # Call custom validator
            result = validator_func(ne_folder_path, ne_name, ne_type, ne_rule)

            # Ensure result has required fields
            if 'deployment_mode' not in result:
                result['deployment_mode'] = None

            return result

        except ImportError as e:
            return {
                'ne_name': ne_name,
                'ne_type': ne_type,
                'valid': False,
                'missing_paths': [],
                'found_paths': [],
                'deployment_mode': None,
                'description': f'Failed to load custom validator: {str(e)}'
            }
        except AttributeError as e:
            return {
                'ne_name': ne_name,
                'ne_type': ne_type,
                'valid': False,
                'missing_paths': [],
                'found_paths': [],
                'deployment_mode': None,
                'description': f'Custom validator function not found: {str(e)}'
            }
        except Exception as e:
            return {
                'ne_name': ne_name,
                'ne_type': ne_type,
                'valid': False,
                'missing_paths': [],
                'found_paths': [],
                'deployment_mode': None,
                'description': f'Custom validator error: {str(e)}'
            }
