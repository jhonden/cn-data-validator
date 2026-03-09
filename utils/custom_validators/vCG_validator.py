# -*- coding: utf-8 -*-
"""
vCG Custom Static MML Validator
vCG 网元自定义静态 MML 校验器

Requires 3 paths to have files.
"""

import os
import glob
from typing import Dict, List


def validate_static_mml(ne_folder_path: str, ne_name: str, ne_type: str, config: Dict) -> Dict:
    """
    vCG static MML validator

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
    # Required paths (all must have files)
    required_paths = [
        'cg/mml/*.txt',
        'vnrs/mml/*.txt',
        '0/mml/*.txt'
    ]

    missing_paths = []
    found_paths = []

    # Check each required path
    for path_pattern in required_paths:
        glob_pattern = os.path.join(ne_folder_path, path_pattern)
        files = glob.glob(glob_pattern)

        if files:
            found_paths.extend(files)
        else:
            missing_paths.append(path_pattern)

    # Determine result
    is_valid = len(missing_paths) == 0

    return {
        'ne_name': ne_name,
        'ne_type': ne_type,
        'valid': is_valid,
        'missing_paths': missing_paths if not is_valid else [],
        'found_paths': found_paths,
        'deployment_mode': None,
        'description': 'Valid' if is_valid else f'missing: {", ".join(missing_paths)}'
    }
