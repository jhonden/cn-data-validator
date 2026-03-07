"""
vUGW Custom Static MML Validator
vUGW 网元自定义静态 MML 校验器

Supports 3 deployment modes (CGW/DGW/UGW).
Each mode requires 4 paths to have files.
Any complete deployment mode passes validation.
"""

import os
import glob
from typing import Dict, List


def validate_static_mml(ne_folder_path: str, ne_name: str, ne_type: str, config: Dict) -> Dict:
    """
    vUGW static MML validator

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
    # Define 3 deployment modes and their check paths
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
    found_paths = []
    found_deployment = None
    found_any_file = False

    # Check each deployment mode
    for deployment_name, deployment in deployments.items():
        deployment_complete = True
        deployment_missing = []
        deployment_found = []

        for path_pattern in deployment['paths']:
            glob_pattern = os.path.join(ne_folder_path, path_pattern)

            # Use glob to find files
            files = glob.glob(glob_pattern)

            if files:
                found_any_file = True
                deployment_found.extend(files)
            else:
                deployment_complete = False
                deployment_missing.append(path_pattern)

        # If all 4 paths have files, record as found deployment
        if deployment_complete:
            found_deployment = deployment_name
            found_paths.extend(deployment_found)
            break  # One complete deployment is enough

    # Determine overall validation result
    is_valid = found_deployment is not None

    if not is_valid:
        # No deployment found
        if not found_any_file:
            # No files at all
            missing_paths.append('No deployment folder found (cgw/dgw/ugw)')
        else:
            # Found some files but no complete deployment
            for deployment_name, deployment in deployments.items():
                for path_pattern in deployment['paths']:
                    glob_pattern = os.path.join(ne_folder_path, path_pattern)
                    if glob.glob(glob_pattern):
                        # This path has files
                        pass
                    else:
                        # This path is missing
                        if path_pattern not in missing_paths:
                            missing_paths.append(path_pattern)

    return {
        'ne_name': ne_name,
        'ne_type': ne_type,
        'valid': is_valid,
        'missing_paths': missing_paths if not is_valid else [],
        'found_paths': found_paths,
        'deployment_mode': found_deployment,  # Only for internal use
        'description': f'Valid ({found_deployment})' if is_valid else f'missing: {", ".join(missing_paths)}'
    }
