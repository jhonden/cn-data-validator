#!/usr/bin/env python3
"""创建非匿名化方式采集的 NIC 包测试数据

预期结果:
- 状态：Valid (绿色)
- 无匿名化相关错误提示
"""

import os
import tarfile
import tempfile
import shutil


def create_non_anonymous_package(output_path='test_data/test_non_anonymous.tar.gz'):
    """创建非匿名化采集的 NIC 包

    Args:
        output_path: 输出文件路径
    """

    # 创建临时目录
    temp_dir = tempfile.mkdtemp(prefix='non_anonymous_')
    print(f"Creating non-anonymous NIC package in: {temp_dir}")

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

    # 创建 XML 文件（非匿名化模式：false）
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<taskInfo taskType="sceneTask" taskExecType="instance" selNEInfo="64:V500R023C10SPC110|56:V500R023C10SPC100|9596:V500R023C10SPH156" selProductType="" isAllVers="false">
    <domainName>CN</domainName>
    <treeDomainName>CN</treeDomainName>
    <StartTime>2025-03-20 21:15:18</StartTime>
    <EndTime>2025-03-27 21:15:18</EndTime>
    <taskDeleteThresholdValue>7</taskDeleteThresholdValue>

    <PeriodExecInfo>
        <ExecutType>allDay</ExecutType>
        <TimeRange>
            <TaskTimeRange>2025-03-20 21:15:18|2025-03-27 21:15:18</TaskTimeRange>
        </TimeRange>
        <CollectRange>2025-03-20 21:15:18|2025-03-27 21:15:18</CollectRange>
        <FileType></FileType>
        <PeriodValue></PeriodValue>
        <ExecDay></ExecDay>
        <TimeValue></TimeValue>
    </PeriodExecInfo>

    <TaskDescription>
        <UserName></UserName>
        <EMail></EMail>
        <Tel></Tel>
        <Operator>HW-BJN-00442769</Operator>
        <Description>create Scenario Task-20250327-211328-WLTE</Description>
        <DownloadByMe>false</DownloadByMe>
        <autoDelete>true</autoDelete>
        <AnonymousAuthMode>false</AnonymousAuthMode>
        <isSoftMode>false</isSoftMode>
        <BatchHD></BatchHD>
        <isCounterPreciseCollection>false</isCounterPreciseCollection>
        <isAutoCollection>true</isAutoCollection>
    </TaskDescription>
</taskInfo>"""

    xml_path = os.path.join(taskparam_dir, 'TaskExtValue.xml')
    with open(xml_path, 'w', encoding='utf-8') as f:
        f.write(xml_content)

    print(f"✓ Created: taskparam/TaskExtValue.xml (AnonymousAuthMode: false)")

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
    print("Create Non-Anonymous Mode NIC Package")
    print("=" * 70)
    print()
    print("This package was collected in non-anonymous mode (AnonymousAuthMode=false).")
    print("Expected validation result:")
    print("  Status: Valid (Green)")
    print("  No anonymous mode related errors")
    print()
    print("=" * 70)
    print()

    # 创建测试包
    output_file = create_non_anonymous_package()

    print("\n" + "=" * 70)
    print("Next Steps:")
    print("=" * 70)
    print(f"\n1. Run validator: python3 validator_qt.py")
    print(f"2. Select the 'test_data' directory")
    print(f"3. Click 'Start Validation'")
    print(f"4. Look for 'test_non_anonymous.tar.gz' in the table")
    print(f"5. Verify Status is 'Valid' (Green)")
    print(f"6. Check that no anonymous mode errors are shown")
    print()
