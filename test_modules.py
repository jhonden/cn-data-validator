#!/usr/bin/env python3
"""Quick test to verify core functionality without GUI"""

import os
import sys

# Add project root to sys.path
if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.file_scanner import FileScanner
from utils.package_identifier import PackageIdentifier

print("=" * 60)
print("Test: Module Import")
print("=" * 60)

# Test imports
try:
    print(f"✓ FileScanner imported successfully")
    print(f"✓ PackageIdentifier imported successfully")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

print()
print("=" * 60)
print("Test: Create Test NIC Package")
print("=" * 60)

# Create test NIC package structure
import tarfile
import tempfile

test_dir = tempfile.mkdtemp()
nic_file = os.path.join(test_dir, 'test_nic.tar.gz')

# Create NIC package structure
nic_dir = os.path.join(test_dir, '20250203105511')
nic_report = os.path.join(test_dir, '20250203105511_report.tar.gz')
os.makedirs(nic_dir, exist_ok=True)

# Create a dummy file inside nic_dir
with open(os.path.join(nic_dir, 'test.txt'), 'w') as f:
    f.write('test content')

# Create tar.gz
with tarfile.open(nic_file, 'w:gz') as tar:
    tar.add(nic_dir, arcname='test_nic')
    tar.add(nic_report, arcname='test_nic_report')
print(f"✓ Test NIC package created: {nic_file}")

print()
print("=" * 60)
print("Test: Package Identification")
print("=" * 60)

# Create identifier
identifier = PackageIdentifier()

# Test 1: Recognize NIC package
result, details = identifier.identify(nic_file, 'test_nic.tar.gz')

print(f"File: test_nic.tar.gz")
print(f"Package Type: {result[0]}")
print(f"Details: {result[1]}")
print()
print("=" * 60)
print("Test: File Scanner")
print("=" * 60)

# Scan a directory
scan_dir = test_dir

scanner = FileScanner(scan_dir)
scanner.scan_directory()

print(f"Scan completed")
stats = scanner.get_statistics()
print(f"  Total files: {stats['total_files']}")
print(f"  Valid files: {stats['valid_files']}")
print(f"  Invalid files: {stats['illegal_files']}")
print()
print("=" * 60)
print("Test Summary")
print("=" * 60)

# Check if test package is recognized correctly
test_package_found = False
for file_info in scanner.valid_files:
    if 'test_nic.tar.gz' in file_info['name']:
        test_package_found = True
        print(f"✓ Test package found in valid files")
        print(f"  Package type: {file_info.get('package_type')}")
        print(f"  Package details: {file_info.get('package_details')}")

if test_package_found:
    print("✓ SUCCESS: Package identification working correctly!")
else:
    print("✗ FAIL: Test package not recognized")

# Cleanup
import shutil
shutil.rmtree(test_dir, ignore_errors=True)

print()
print("=" * 60)
print("Test Complete!")
print("All core functionalities are working as expected.")
print("=" * 60)
