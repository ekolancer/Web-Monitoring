"""
Custom exceptions for WEB-MON
"""


class WebMonError(Exception):
    """Base exception for WEB-MON"""
    pass


class ConfigurationError(WebMonError):
    """Configuration related errors"""
    pass


class MonitoringError(WebMonError):
    """Monitoring related errors"""
    pass


class NetworkError(MonitoringError):
    """Network connectivity errors"""
    pass


class SSLError(MonitoringError):
    """SSL/TLS related errors"""
    pass


class GoogleSheetsError(WebMonError):
    """Google Sheets integration errors"""
    pass


class NotificationError(WebMonError):
    """Notification system errors"""
    pass


class TelegramError(NotificationError):
    """Telegram notification errors"""
    pass


class EmailError(NotificationError):
    """Email notification errors"""
    pass


class SecurityCheckError(WebMonError):
    """Security check related errors"""
    pass


class ValidationError(WebMonError):
    """Data validation errors"""
    pass
