# -*- coding: utf-8 -*-
"""自定义异常类定义"""


class ValidationException(Exception):
    """验证异常基类

    Attributes:
        message: 错误消息
        error_type: 错误类型标识符
        suggestion: 解决建议
    """

    def __init__(self, message, error_type, suggestion=None):
        self.message = message
        self.error_type = error_type
        self.suggestion = suggestion
        super().__init__(message)


class DirectoryNotFoundException(ValidationException):
    """目录不存在异常"""

    def __init__(self, path):
        message = f"Directory not found: {path}"
        suggestion = "Please check if the directory path is correct"
        super().__init__(message, "directory_not_found", suggestion)


class PermissionDeniedException(ValidationException):
    """权限拒绝异常"""

    def __init__(self, path):
        message = f"Permission denied: {path}"
        suggestion = "Please check if you have the required permissions to access this directory"
        super().__init__(message, "permission_denied", suggestion)


class InvalidPackageException(ValidationException):
    """无效数据包异常"""

    def __init__(self, message):
        suggestion = "Please check if the data package format meets the requirements"
        super().__init__(message, "invalid_package", suggestion)


class FileSystemException(ValidationException):
    """文件系统异常"""

    def __init__(self, message, suggestion=None):
        if suggestion is None:
            suggestion = "Please check if there are sufficient disk space and the file system is healthy"
        super().__init__(message, "file_system_error", suggestion)


class MemoryException(ValidationException):
    """内存不足异常"""

    def __init__(self):
        message = "Insufficient memory to complete the validation"
        suggestion = "Please close other applications or upgrade your system memory"
        super().__init__(message, "memory_error", suggestion)
