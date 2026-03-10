        """Display results"""
        stats = self.scanner.get_statistics()

        # Check if no files found
        if stats['total_files'] == 0:
            # Display empty state
            self.table.setRowCount(1)
            empty_item = QTableWidgetItem("No files found in the selected directory")
            empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_item.setForeground(QColor("#999999"))
            empty_item.setFont(QFont("Arial", 12, QFont.Weight.Normal))
            self.table.setItem(0, 0, empty_item)
            self.table.setSpan(0, 0, 1, 7)  # Merge all columns

            # Update statistics
            self.stats_label.setText("Total: 0 files | Valid: 0 | Invalid: 0")
            self.statusBar.showMessage("Scan completed: No files found")
            self.export_btn.setEnabled(False)

            QMessageBox.information(
                self,
                "Scan Completed",
                "No files found in the selected directory.\n\n"
                "Please select a different directory that contains data package files."
            )
            return

        # 保存原始数据用于筛选
        self.all_valid_files = []
        for file_info in self.scanner.valid_files:
            # Get package type and details
            package_type = file_info.get('package_type', 'Unknown')
            package_details = file_info.get('package_details', {})

            # Set color based on package type
            if package_type == 'NIC Package':
                package_color = '#2196F3'  # Blue
            elif package_type == 'Unknown':
                package_color = '#FF9800'  # Orange
            else:
                package_color = '#666666'  # Gray

            # Generate detail information
            detail = ''
            status = 'Valid'
            status_color = '#4CAF50'

            if package_type == 'NIC Package':
                time = package_details.get('time', '')
                if time:
                    detail = f'Time: {time}'

                # 处理 NIC 校验结果
