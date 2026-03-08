"""
Scenario Checker
网元采集场景校验器

Validates collection scenarios for network elements (NEs) by checking:
- scenario_group_name from taskinfo.txt against expected scenarios
- Special handling for USCDB (version format determines expected scenario)
"""

import os
import re
from typing import Dict, List, Optional
import yaml
import xml.etree.ElementTree as ET


class ScenarioChecker:
    """Collection Scenario Checker"""

    def __init__(self, config_path: str):
        """
        Initialize checker and load configuration

        Args:
            config_path: Path to scenario configuration file (scenario_config.yaml)
        """
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load configuration file"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def check_package(self, ne_parent_path: str, ne_instances: List) -> Dict:
        """
        Check collection scenarios for all NEs in a package

        Args:
            ne_parent_path: NE data parent folder path (containing all NE folders)
            ne_instances: List of NEInstance objects

        Returns:
            {
                'total_ne_count': int,
                'valid_ne_count': int,
                'invalid_ne_count': int,
                'ne_results': List[Dict]
            }
        """
        # Check each NE
        results = []
        for ne_instance in ne_instances:
            result = self._check_ne(ne_parent_path, ne_instance)
            results.append(result)

        # Aggregate results
        return {
            'total_ne_count': len(results),
            'valid_ne_count': sum(1 for r in results if r['valid'] is True),
            'invalid_ne_count': sum(1 for r in results if r['valid'] is False),
            'ne_results': results
        }

    def _check_ne(self, ne_parent_path: str, ne_instance) -> Dict:
        """
        Check collection scenario for a single NE

        Args:
            ne_parent_path: NE data parent folder path
            ne_instance: NEInstance object

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
        ne_type = ne_instance.ne_type
        ne_name = ne_instance.name

        # Get expected scenario
        expected_scenario = None
        if ne_type == 'USCDB':
            # Special handling for USCDB - check version format first
            ne_folder_path = os.path.join(ne_parent_path, ne_instance.folder_name)
            expected_scenario = self._get_uscdb_expected_scenario(ne_folder_path)
        else:
            # Standard handling for other NE types
            expected_scenario_info = self.config.get('scenarios', {}).get(ne_type, {})
            expected_scenario = expected_scenario_info.get('en', '')

        if not expected_scenario:
            return {
                'ne_name': ne_name,
                'ne_type': ne_type,
                'valid': True,  # Not configured, skip validation
                'expected_scenario': None,
                'actual_scenario': None,
                'error': None
            }

        # Get actual scenario from taskinfo.txt
        actual_scenario = self._read_scenario_from_taskinfo(ne_parent_path)
        if actual_scenario is None:
            return {
                'ne_name': ne_name,
                'ne_type': ne_type,
                'valid': True,  # No scenario info, skip validation
                'expected_scenario': expected_scenario,
                'actual_scenario': None,
                'error': None
            }

        # Compare scenarios
        if actual_scenario != expected_scenario:
            error_msg = self._format_scenario_error(ne_type, ne_name, expected_scenario, actual_scenario)
            return {
                'ne_name': ne_name,
                'ne_type': ne_type,
                'valid': False,
                'expected_scenario': expected_scenario,
                'actual_scenario': actual_scenario,
                'error': error_msg
            }

        return {
            'ne_name': ne_name,
            'ne_type': ne_type,
            'valid': True,
            'expected_scenario': expected_scenario,
            'actual_scenario': actual_scenario,
            'error': None
        }

    def _get_uscdb_expected_scenario(self, ne_folder_path: str) -> Optional[str]:
        """
        Get expected scenario for USCDB based on version format

        Args:
            ne_folder_path: NE data folder path (e.g., /path/USCDB_NE=1_IP_xxx_xxx_xxx_name)

        Returns:
            Expected scenario name based on version format, None if not found
        """
        try:
            # Read NeAllinfos.xml from NE folder
            neallinfos_path = os.path.join(ne_folder_path, 'NeAllinfos.xml')
            if not os.path.exists(neallinfos_path):
                return None

            # Parse XML and extract neVersion
            tree = ET.parse(neallinfos_path)
            root = tree.getroot()

            # Find neVersion element
            ne_version = None
            for neinfo in root.findall('NeInfo'):
                version_elem = neinfo.find('neVersion')
                if version_elem is not None and version_elem.text:
                    ne_version = version_elem.text.strip()
                    break

            if not ne_version:
                return None

            # Determine version format
            # VRC format: starts with 'V' followed by letters/numbers (e.g., V500R020C10)
            # Dotted format: contains dots (e.g., 20.3.2)
            if ne_version.startswith('V') and re.match(r'^V\d+[A-Za-z]\d+', ne_version):
                # VRC format - use offline health check scenario
                return 'Offline health check scenario'
            elif '.' in ne_version:
                # Dotted format - use cloud health check scenario
                return 'Cloud health check scenario'
            else:
                # Unknown format - default to offline
                return 'Offline health check scenario'

        except Exception:
            return None

    def _read_scenario_from_taskinfo(self, ne_parent_path: str) -> Optional[str]:
        """
        Read scenario from taskinfo.txt

        Args:
            ne_parent_path: NE data parent folder path

        Returns:
            Scenario name, None if not found
        """
        taskinfo_path = os.path.join(ne_parent_path, 'taskinfo.txt')
        if not os.path.exists(taskinfo_path):
            return None

        try:
            with open(taskinfo_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('scenario_group_name='):
                        # Extract scenario name after '=' and before ';'
                        scenario_part = line.split('=')[1].split(';')[0]
                        return scenario_part
        except Exception:
            pass

        return None

    def _format_scenario_error(self, ne_type: str, ne_name: str, expected_scenario: str, actual_scenario: str) -> str:
        """
        Format scenario error message

        Args:
            ne_type: NE type
            ne_name: NE instance name
            expected_scenario: Expected scenario name
            actual_scenario: Actual scenario name

        Returns:
            Formatted error message
        """
        # Get language from config (default to English)
        ui_language = self.config.get('ui_language', 'en')

        if ui_language == 'zh':
            return f"网元采集场景错误：网元'{ne_name}'（{ne_type}）应该使用'{expected_scenario}'采集场景"
        else:
            return f"Collection scenario error: NE '{ne_name}' ({ne_type}) should use '{expected_scenario}' collection scenario"
