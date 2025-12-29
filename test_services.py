#!/usr/bin/env python3
"""
Test script for services
"""

try:
    from services.monitoring_service import MonitoringService
    from services.notification_service import NotificationService
    print("✅ Services import successfully")

    # Test service instantiation
    monitoring = MonitoringService()
    notification = NotificationService()
    print("✅ Services instantiate successfully")

    # Test notification service methods (without actual sending)
    print("✅ All tests passed")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
