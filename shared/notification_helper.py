"""
Reusable Notification Helper for ServEase Microservices
--------------------------------------------------------
This module provides a centralized way to send notifications across all microservices.
Following DRY principles, all services should use this helper instead of duplicating code.

Usage Example:
    from shared.notification_helper import NotificationHelper
    
    # Send a simple notification
    NotificationHelper.send(
        user_id=123,
        message="Your appointment has been confirmed",
        notification_type=NotificationHelper.APPOINTMENT
    )
    
    # Send to multiple users
    NotificationHelper.send_bulk(
        user_ids=[123, 456, 789],
        message="System maintenance scheduled",
        notification_type=NotificationHelper.SYSTEM
    )
"""

import requests
from typing import List, Optional, Dict, Any
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class NotificationHelper:
    """
    Centralized notification helper for all ServEase microservices.
    Supports both HTTP API (persistent storage) and WebSocket (real-time push).
    """
    
    # Notification service endpoint
    NOTIFICATION_SERVICE_URL = 'http://notification-service:8006/api/v1/notifications/'
    
    # Notification types (matching the model choices)
    SYSTEM = 'SYSTEM'
    APPOINTMENT = 'APPOINTMENT'
    VEHICLE = 'VEHICLE'
    OTHER = 'OTHER'
    
    @staticmethod
    def send(
        user_id: int,
        message: str,
        notification_type: str = OTHER,
        store_in_db: bool = True,
        send_realtime: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send a notification to a single user.
        
        Args:
            user_id: The recipient's user ID
            message: The notification message text
            notification_type: Type of notification (SYSTEM, APPOINTMENT, VEHICLE, OTHER)
            store_in_db: Whether to store in database (default: True)
            send_realtime: Whether to send via WebSocket (default: True)
            metadata: Optional additional data to include
            
        Returns:
            bool: True if at least one method succeeded, False if both failed
        """
        success = False
        
        # Store in database via HTTP API
        if store_in_db:
            try:
                payload = {
                    'recipient_user_id': user_id,
                    'message': message,
                    'type': notification_type
                }
                
                response = requests.post(
                    NotificationHelper.NOTIFICATION_SERVICE_URL,
                    json=payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=5
                )
                
                if response.status_code == 201:
                    logger.info(f"Notification stored for user {user_id}")
                    success = True
                else:
                    logger.error(
                        f"Failed to store notification for user {user_id}: "
                        f"Status {response.status_code}"
                    )
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Error storing notification for user {user_id}: {e}")
        
        # Send real-time push via WebSocket
        if send_realtime:
            try:
                channel_layer = get_channel_layer()
                
                if channel_layer:
                    notification_data = {
                        'message': message,
                        'type': notification_type,
                        'timestamp': datetime.utcnow().isoformat(),
                    }
                    
                    if metadata:
                        notification_data['metadata'] = metadata
                    
                    async_to_sync(channel_layer.group_send)(
                        f'notifications_{user_id}',
                        {
                            'type': 'send_notification',
                            'message': notification_data
                        }
                    )
                    
                    logger.info(f"Real-time notification sent to user {user_id}")
                    success = True
                else:
                    logger.warning("Channel layer not available for real-time notifications")
                    
            except Exception as e:
                logger.error(f"Error sending real-time notification to user {user_id}: {e}")
        
        return success
    
    @staticmethod
    def send_bulk(
        user_ids: List[int],
        message: str,
        notification_type: str = OTHER,
        store_in_db: bool = True,
        send_realtime: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, int]:
        """
        Send the same notification to multiple users.
        
        Args:
            user_ids: List of recipient user IDs
            message: The notification message text
            notification_type: Type of notification
            store_in_db: Whether to store in database
            send_realtime: Whether to send via WebSocket
            metadata: Optional additional data to include
            
        Returns:
            dict: Statistics with 'success' and 'failed' counts
        """
        stats = {'success': 0, 'failed': 0}
        
        for user_id in user_ids:
            success = NotificationHelper.send(
                user_id=user_id,
                message=message,
                notification_type=notification_type,
                store_in_db=store_in_db,
                send_realtime=send_realtime,
                metadata=metadata
            )
            
            if success:
                stats['success'] += 1
            else:
                stats['failed'] += 1
        
        logger.info(
            f"Bulk notification sent: {stats['success']} succeeded, "
            f"{stats['failed']} failed"
        )
        
        return stats
    
    @staticmethod
    def notify_appointment_created(customer_id: int, appointment_details: Dict[str, Any]) -> bool:
        """Helper method for appointment creation notifications"""
        message = (
            f"Your appointment has been scheduled for "
            f"{appointment_details.get('date', 'TBD')} "
            f"at {appointment_details.get('time', 'TBD')}"
        )
        
        return NotificationHelper.send(
            user_id=customer_id,
            message=message,
            notification_type=NotificationHelper.APPOINTMENT,
            metadata=appointment_details
        )
    
    @staticmethod
    def notify_appointment_updated(customer_id: int, changes: str) -> bool:
        """Helper method for appointment update notifications"""
        message = f"Your appointment has been updated: {changes}"
        
        return NotificationHelper.send(
            user_id=customer_id,
            message=message,
            notification_type=NotificationHelper.APPOINTMENT
        )
    
    @staticmethod
    def notify_appointment_cancelled(customer_id: int, reason: str = "N/A") -> bool:
        """Helper method for appointment cancellation notifications"""
        message = f"Your appointment has been cancelled. Reason: {reason}"
        
        return NotificationHelper.send(
            user_id=customer_id,
            message=message,
            notification_type=NotificationHelper.APPOINTMENT
        )
    
    @staticmethod
    def notify_vehicle_status_changed(customer_id: int, vehicle_info: str, new_status: str) -> bool:
        """Helper method for vehicle status change notifications"""
        message = f"Vehicle {vehicle_info} status changed to: {new_status}"
        
        return NotificationHelper.send(
            user_id=customer_id,
            message=message,
            notification_type=NotificationHelper.VEHICLE
        )
    
    @staticmethod
    def notify_system_alert(user_ids: List[int], alert_message: str) -> Dict[str, int]:
        """Helper method for system-wide alerts"""
        return NotificationHelper.send_bulk(
            user_ids=user_ids,
            message=alert_message,
            notification_type=NotificationHelper.SYSTEM
        )
