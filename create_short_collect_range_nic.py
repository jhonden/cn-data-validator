#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""创建采集时间范围小于24小时的 NIC 包测试数据

预期结果:
- 状态：Invalid (红色)
- 提示：NIC package collection time range is too short, cannot support network assessment requirements.
        System requires at least 24h, please re-collect. (Actual: 12.5h)
"""

import os
import tarfile
import tempfile
import shutil
import xml.etree.ElementTree as ET


def create_short_collect_range_package(output_path='test_data/test_short_collect_range.tar.gz'):
    """创建采集时间范围小于24小时的 NIC 包

    Args:
        output_path: 输出文件路径
    """

    # 创建临时目录
    temp_dir = tempfile.mkdtemp(prefix='short_collect_')
    print(f"Creating short collect range NIC package in: {temp_dir}")

    # 创建时间文件夹
    time_folder = "20250320211518"
    time_dir = os.path.join(temp_dir, time_folder)
    os.makedirs(time_dir, exist_ok=True)

    # 创建 neinfo.txt
    neinfo_path = os.path.join(time_dir, 'neinfo.txt')
    with open(neinfo_path, 'w', encoding='utf-8') as f:
        f.write("PPR_CSCF01   CSCF_NE=1094   56   10.140.2.1\n")
        f.write("PPR_ATS01   ATS_NE=1044   59   10.140.2.10\n")

    print("✓ Created neinfo.txt with 2 NE instances")

    # 创建网元数据文件夹
    ne_folders = [
        ('CSCF_NE=1094', '10.140.2.1', '56', 'PPR_CSCF01'),
        ('ATS_NE=1044', '10.140.2.10', '59', 'PPR_ATS01'),
    ]

    for ne_type_id, ip, group, name in ne_folders:
        ip_formatted = ip.replace('.', '_')
        folder_name = f"{ne_type_id}_IP_{ip_formatted}_{group}_{name}"
        folder_path = os.path.join(time_dir, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        # 创建必需文件
        with open(os.path.join(folder_path, 'static_mml.txt'), 'w') as f:
            f.write(f'Static MML config for {name}')
        with open(os.path.join(folder_path, 'dynamic_mml.txt'), 'w') as f:
            f.write(f'Dynamic MML config for {name}')
        with open(os.path.join(folder_path, 'statistics.txt'), 'w') as f:
            f.write(f'Statistics data for {name}')

        print(f"✓ Created: {folder_name}")

    # 创建 report.tar.gz
    report_dir = os.path.join(temp_dir, 'temp_report')
    os.makedirs(report_dir, exist_ok=True)

    # 创建 taskparam/TaskExtValue.xml
    taskparam_dir = os.path.join(report_dir, 'taskparam')
    os.makedirs(taskparam_dir, exist_ok=True)

    # 创建 XML 文件（采集时间范围：12.5小时，小于24小时）
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<taskInfo taskType="sceneTask" taskExecType="instance" sellNEVer="...">
    <domainName>CN</domainName>
    <treeDomainName>CN</treeDomainName>
    <StartTime>2025-03-20 21:15:18</StartTime>
    <EndTime>2025-03-21 09:45:18</EndTime>
    <taskDeleteThresholdValue>7</taskDeleteThresholdValue>
    <PeriodExecInfo>
        <ExecuteType>allDay</ExecuteType>
        <AMTimeRange/>
        <PMTimeRange/>
        <TaskTimeRange>2025-03-20 21:15:18|2025-03-21 09:45:18</TaskTimeRange>
        <CollectRange>2025-03-20 21:15:18|2025-03-21 09:45:18</CollectRange>
        <FileSaveDay/>
        <PeriodType/>
        <PeriodValue/>
        <ExecDay/>
        <ExecTime/>
    </PeriodExecInfo>
</taskInfo>"""

    xml_path = os.path.join(taskparam_dir, 'TaskExtValue.xml')
    with open(xml_path, 'w', encoding='utf-8') as f:
        f.write(xml_content)

    print(f"✓ Created: taskparam/TaskExtValue.xml (CollectRange: 12.5h)")

    # 打包 report.tar.gz
    report_path = os.path.join(temp_dir, f'{time_folder}_report.tar.gz')
    with tarfile.open(report_path, 'w:gz') as tar:
        tar.add(taskparam_dir, arcname='taskparam')

    print(f"✓ Created report file: {os.path.basename(report_path)}")

    # 清理临时 report 目录
    shutil.rmtree(report_dir, ignore_errors=True)

    # 确保输出目录存在
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)

    # 打包成 tar.gz
    with tarfile.open(output_path, 'w:gz') as tar:
        tar.add(time_dir, arcname=time_folder)
        tar.add(report_path, arcname=os.path.basename(report_path))

    print(f"\n✓ Test NIC package created: {output_path}")
    print(f"  File size: {os.path.getsize(output_path) / 1024:.2f} KB")

    # 清理临时目录
    shutil.rmtree(temp_dir, ignore_errors=True)
    print(f"✓ Cleaned up temporary directory")

    return output_path


if __name__ == '__main__':
    print("=" * 70)
    print("Create Short Collect Range NIC Package")
    print("=" * 70)
    print()
    print("This package has a collection time range of 12.5h (< 24h).")
    print("Expected validation result:")
    print("  Status: Invalid (Red)")
    print("  Message: NIC package collection time range is too short, cannot support")
    print("           network assessment requirements. System requires at least 24h,")
    print("           please re-collect. (Actual: 12.5h)")
    print()
    print("=" * 70)
    print()

    # 创建测试包
    output_file = create_short_collect_range_package()

    print("\n" + "=" * 70)
    print("Next Steps:")
    print("=" * 70)
    print(f"\n1. Run validator: python3 validator_qt.py")
    print(f"2. Select the 'test_data' directory")
    print(f"3. Click 'Start Validation'")
    print(f"4. Look for 'test_short_collect_range.tar.gz' in the table")
    print(f"5. Verify Status is 'Invalid' (Red)")
    print(f"6. Check Details column for the error message")
    print()
