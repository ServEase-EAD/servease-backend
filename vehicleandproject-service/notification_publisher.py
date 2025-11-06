"""
RabbitMQ Notification Publisher
================================
Lightweight client for publishing notifications to the notification service via RabbitMQ.

This file can be copied to any microservice that needs to send notifications.
No dependencies on the notification service code - just pure RabbitMQ client.

Requirements:
    pip install pika

Usage:
    from notification_publisher import publish_notification
    
    publish_notification(
        recipient_user_id=1,
        message="Your order is ready!",
        title="Order Update",
        priority="high"
    )
"""

import pika
import json
import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# RabbitMQ Configuration (set these in your service's environment)
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'admin')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'admin123')
QUEUE_NAME = 'notification_events'


def publish_notification(
    recipient_user_id: str,
    message: str,
    title: Optional[str] = None,
    priority: str = 'medium',
    notification_type: str = 'OTHER',
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Publish a notification event to RabbitMQ.
    
    Args:
        recipient_user_id: User ID (UUID string) to send notification to
        message: Notification message
        title: Optional notification title
        priority: Priority level (low, medium, high)
        notification_type: Type (SYSTEM, APPOINTMENT, VEHICLE, OTHER)
        metadata: Optional additional data
        
    Returns:
        bool: True if published successfully, False otherwise
        
    Example:
        success = publish_notification(
            recipient_user_id=123,
            message="Your appointment is confirmed",
            title="Appointment Confirmed",
            priority="high",
            notification_type="APPOINTMENT"
        )
    """
    try:
        # Connect to RabbitMQ
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        parameters = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        
        # Prepare event payload
        event = {
            'recipient_user_id': recipient_user_id,
            'message': message,
            'title': title,
            'priority': priority,
            'notification_type': notification_type,
            'metadata': metadata or {}
        }
        
        # Publish to queue
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=json.dumps(event),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Persistent
                content_type='application/json'
            )
        )
        
        connection.close()
        logger.info(f"✓ Notification published for user {recipient_user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to publish notification: {e}")
        return False


def publish_bulk_notifications(notifications: list) -> int:
    """
    Publish multiple notifications in batch.
    
    Args:
        notifications: List of notification dicts
        
    Returns:
        int: Number of successfully published notifications
        
    Example:
        notifications = [
            {"recipient_user_id": 1, "message": "Message 1", "priority": "high"},
            {"recipient_user_id": 2, "message": "Message 2", "priority": "medium"},
        ]
        count = publish_bulk_notifications(notifications)
    """
    success_count = 0
    
    try:
        # Reuse connection for batch
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        parameters = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            credentials=credentials,
            heartbeat=600
        )
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        
        for notification in notifications:
            try:
                event = {
                    'recipient_user_id': notification.get('recipient_user_id'),
                    'message': notification.get('message'),
                    'title': notification.get('title'),
                    'priority': notification.get('priority', 'medium'),
                    'notification_type': notification.get('notification_type', 'OTHER'),
                    'metadata': notification.get('metadata', {})
                }
                
                channel.basic_publish(
                    exchange='',
                    routing_key=QUEUE_NAME,
                    body=json.dumps(event),
                    properties=pika.BasicProperties(delivery_mode=2)
                )
                success_count += 1
                
            except Exception as e:
                logger.error(f"Failed to publish notification: {e}")
                
        connection.close()
        logger.info(f"✓ Published {success_count}/{len(notifications)} notifications")
        
    except Exception as e:
        logger.error(f"Failed to connect to RabbitMQ: {e}")
        
    return success_count


# Convenience functions for common notification types
def notify_project_created(user_id: str, project_details: Dict[str, Any]) -> bool:
    """Send project creation notification"""
    return publish_notification(
        recipient_user_id=user_id,
        message=f"New project '{project_details.get('title', 'Untitled')}' has been created and requires approval.",
        title="New Project Created",
        priority="high",
        notification_type="PROJECT",
        metadata=project_details
    )


def notify_vehicle_status_changed(user_id: str, vehicle_id: str, new_status: str) -> bool:
    """Send vehicle status change notification"""
    return publish_notification(
        recipient_user_id=user_id,
        message=f"Vehicle {vehicle_id} status changed to: {new_status}",
        title="Vehicle Status Update",
        priority="medium",
        notification_type="VEHICLE"
    )


def notify_system_alert(user_ids: list, message: str) -> int:
    """Send system alert to multiple users"""
    notifications = [
        {
            'recipient_user_id': user_id,
            'message': message,
            'title': 'System Alert',
            'priority': 'high',
            'notification_type': 'SYSTEM'
        }
        for user_id in user_ids
    ]
    return publish_bulk_notifications(notifications)