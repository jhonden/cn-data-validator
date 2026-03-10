#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate test NIC packages for scenario validation testing
"""

import os
import tarfile
import tempfile
import shutil

def create_test_package(package_name, ne_list, scenario_name):
    temp_dir = tempfile.mkdtemp(prefix='scenario_test_')
    print(f"Creating NIC package in: {temp_dir}")

    time_folder = "20250308000000"
    time_dir = os.path.join(temp_dir, time_folder)
    os.makedirs(time_dir, exist_ok=True)

    # Create neinfo.txt
    neinfo_content = ""
    for ne_type, instance_id, group_id, ip, ne_name in ne_list:
        neinfo_content += f"{ne_name}   {ne_type}_NE={instance_id}   {group_id}   {ip}\n"
    
    with open(os.path.join(time_dir, 'neinfo.txt'), 'w', encoding='utf-8') as f:
        f.write(neinfo_content)
    print(f"✓ Created neinfo.txt with {len(ne_list)} NE instances")

    # Create taskinfo.txt
    taskinfo_content = f"scenario_group_name={scenario_name};\n"
    with open(os.path.join(time_dir, 'taskinfo.txt'), 'w', encoding='utf-8') as f:
        f.write(taskinfo_content)
    print(f"✓ Created taskinfo.txt with scenario: {scenario_name}")

    # Create NE folders
    for ne_type, instance_id, group_id, ip, ne_name in ne_list:
        ip_formatted = ip.replace('.', '_')
        ne_folder_name = f"{ne_type}_NE={instance_id}_IP_{ip_formatted}_{group_id}_{ne_name}"
        ne_folder_path = os.path.join(time_dir, ne_folder_name)
        os.makedirs(ne_folder_path, exist_ok=True)

        # Create NeAllinfos.xml for USCDB
        if ne_type == 'USCDB':
            version = 'V500R020C10' if 'vrc' in package_name else '23.1.0.18'
            neallinfos_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<root>
  <NeInfo>
    <neName>{ne_name}</neName>
    <neVersion>{version}</neVersion>
  </NeInfo>
</root>'''
            with open(os.path.join(ne_folder_path, 'NeAllinfos.xml'), 'w', encoding='utf-8') as f:
                f.write(neallinfos_content)

        # Create static MML files
        if ne_type in ['vCG', 'vUSN', 'vUGW']:
            for sub in ['omo', 'vnrs', '0']:
                sub_dir = os.path.join(ne_folder_path, sub, 'mml')
                os.makedirs(sub_dir, exist_ok=True)
                with open(os.path.join(sub_dir, f'{sub}_config.txt'), 'w') as f:
                    f.write(f'{sub} config\n')
            
            if ne_type == 'vCG':
                cg_dir = os.path.join(ne_folder_path, 'cg', 'mml')
                os.makedirs(cg_dir, exist_ok=True)
                with open(os.path.join(cg_dir, 'cg_config.txt'), 'w') as f:
                    f.write('CG config\n')
            elif ne_type == 'vUGW':
                ugw_dir = os.path.join(ne_folder_path, 'ugw', 'mml')
                os.makedirs(ugw_dir, exist_ok=True)
                with open(os.path.join(ugw_dir, 'ugw_config.txt'), 'w') as f:
                    f.write('UGW config\n')
            else:
                usn_dir = os.path.join(ne_folder_path, 'usn', 'mml')
                os.makedirs(usn_dir, exist_ok=True)
                with open(os.path.join(usn_dir, 'usn_config.txt'), 'w') as f:
                    f.write('USN config\n')
        else:
            data_dir = os.path.join(ne_folder_path, 'dataconfiguration')
            os.makedirs(data_dir, exist_ok=True)
            with open(os.path.join(data_dir, 'ALLME.txt'), 'w') as f:
                f.write(f'{ne_type} MML configuration\n')
        print(f"✓ Created NE folder: {ne_folder_name}")

    # Create report.tar.gz
    report_dir = os.path.join(temp_dir, 'temp_report')
    os.makedirs(report_dir, exist_ok=True)
    taskparam_dir = os.path.join(report_dir, 'taskparam')
    os.makedirs(taskparam_dir, exist_ok=True)
    with open(os.path.join(taskparam_dir, 'TaskExtValue.xml'), 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?><taskInfo taskType="sceneTask" taskExecType="instance"><domainName>CN</domainName></taskInfo>')
    report_path = os.path.join(temp_dir, f'{time_folder}_report.tar.gz')
    with tarfile.open(report_path, 'w:gz') as tar:
        tar.add(taskparam_dir, arcname='taskparam')
    shutil.rmtree(report_dir, ignore_errors=True)
    print(f"✓ Created report file: {time_folder}_report.tar.gz")

    # Package
    output_dir = 'test_data'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{package_name}.tar.gz")
    with tarfile.open(output_path, 'w:gz') as tar:
        tar.add(time_dir, arcname=time_folder)
        tar.add(report_path, arcname=os.path.basename(report_path))
    print(f"\n✓ Test NIC package created: {output_path}")
    print(f"  File size: {os.path.getsize(output_path) / 1024:.2f} KB")
    shutil.rmtree(temp_dir, ignore_errors=True)
    return output_path

if __name__ == "__main__":
    print("=" * 70)
    print("Create Test NIC Packages for Scenario Validation")
    print("=" * 70)
    print()

    # Test 1: Correct scenarios
    print("=" * 70)
    print("Test 1: NEs with CORRECT scenarios")
    print("=" * 70)

    ne_list_cscf_ats = [('CSCF', '1094', 'PPR_CSCF01', '10.140.2.1', 'CSCF01'), ('ATS', '1044', 'PPR_ATS01', '10.140.2.10', 'ATS01')]
    create_test_package("test_scenario_correct_cscf_ats", ne_list_cscf_ats, "Offline health check scenario")

    ne_list_udg = [('UDG', '1001', 'PPR_UDG01', '10.140.3.1', 'UDG01')]
    create_test_package("test_scenario_correct_udg", ne_list_udg, "Cloud health check scenario")

    ne_list_v = [('vCG', '3001', 'PPR_CG01', '10.140.2.30', 'CG01'), ('vUGW', '2001', 'PPR_UGW01', '10.140.2.20', 'UGW01')]
    create_test_package("test_scenario_correct_v_ne", ne_list_v, "Health check scenario")

    print("\n" + "=" * 70)
    print("Test 2: NEs with INCORRECT scenarios")
    print("=" * 70)

    create_test_package("test_scenario_wrong_cscf_ats", ne_list_cscf_ats, "Cloud health check scenario")
    create_test_package("test_scenario_wrong_v_ne", ne_list_v, "Offline health check scenario")
    create_test_package("test_scenario_wrong_udg", ne_list_udg, "Offline health check scenario")

    print("\n" + "=" * 70)
    print("All test packages created successfully in tests/data/test_data/ directory!")
    print("=" * 70)
