"""
USCDB Custom Static MML Validator
USCDB 网元自定义静态 MML 校验器

Two validation sets - either one passes validation.
"""

import os
import glob
from typing import Dict, List


def validate_static_mml(ne_folder_path: str, ne_name: str, ne_type: str, config: Dict) -> Dict:
    """
    USCDB static MML validator

    Args:
        ne_folder_path: NE data folder path
        ne_name: NE instance name
        ne_type: NE type
        config: Configuration information

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
    # Two validation sets (match any)
    validation_sets = [
        {
            'name': 'Set 1',
            'path': 'uscdb/dataconfiguration/ALLMML',
            'patterns': ['*.zip', '*.tar.gz', 'ALLME_*.txt']
        },
        {
            'name': 'Set 2',
            'path': 'dataconfiguration',
            'patterns': ['*.zip', '*.tar.gz', 'ALLME_*.txt']
        }
    ]

    missing_paths = []
    found_paths = []
    found_set = None

    # Check each validation set
    for validation_set in validation_sets:
        path = os.path.join(ne_folder_path, validation_set['path'])
        patterns = validation_set['patterns']

        # Check if path exists
        if not os.path.exists(path):
            continue

        # Check patterns (any match passes)
        set_found = False
        for pattern in patterns:
            glob_pattern = os.path.join(path, pattern)
            files = glob.glob(glob_pattern)

            if files:
                found_paths.extend(files)
                set_found = True
                break  # One match is enough for this set

        if set_found:
            found_set = validation_set['name']
            break  # One complete set is enough

    # Determine result
    is_valid = found_set is not None

    if not is_valid:
        # No set found - report both sets as missing
        for validation_set in validation_sets:
            for pattern in validation_set['patterns']:
                missing_paths.append(f"{validation_set['path']}/{pattern}")

    return {
        'ne_name': ne_name,
        'ne_type': ne_type,
        'valid': is_valid,
        'missing_paths': missing_paths if not is_valid else [],
        'found_paths': found_paths,
        'deployment_mode': found_set,  # Store which set was found
        'description': f'Valid ({found_set})' if is_valid else f'missing: {", ".join(missing_paths[:3])}...'
    }
