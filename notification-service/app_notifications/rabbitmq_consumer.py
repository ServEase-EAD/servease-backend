"""
RabbitMQ Consumer for Notification Service
Listens for notification events from other microservices and processes them
"""

import pika
import json
import os
import time
import logging
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notification_service.settings')
django.setup()

from app_notifications.models import Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)

# RabbitMQ Configuration
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'admin')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'admin123')
QUEUE_NAME = 'notification_events'


def get_rabbitmq_connection():
    """Establish connection to RabbitMQ with retry logic"""
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
            parameters = pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            connection = pika.BlockingConnection(parameters)
            logger.info(f"✓ Connected to RabbitMQ at {RABBITMQ_HOST}")
            return connection
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise


def process_notification_event(ch, method, properties, body):
    """
    Process incoming notification events from RabbitMQ
    """
    try:
        # Parse the event
        event = json.loads(body)
        logger.info(f"📬 Received notification event: {event}")
        
        # Extract data
        recipient_user_id = event.get('recipient_user_id')
        title = event.get('title', 'Notification')
        message = event.get('message')
        priority = event.get('priority', 'medium')
        notification_type = event.get('notification_type', 'OTHER')
        
        # Validate required fields
        if not recipient_user_id or not message:
            logger.error(f"Invalid notification event: missing required fields")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        
        # Create notification in database
        notification = Notification.objects.create(
            recipient_user_id=recipient_user_id,
            message=message,
            type=notification_type.upper() if notification_type else 'OTHER'
        )
        
        logger.info(f"✓ Created notification {notification.id} for user {recipient_user_id}")
        
        # Send real-time notification via WebSocket
        try:
            channel_layer = get_channel_layer()
            user_group_name = f'notifications_{recipient_user_id}'
            
            async_to_sync(channel_layer.group_send)(
                user_group_name,
                {
                    'type': 'send_notification',
                    'message': {
                        'id': str(notification.id),
                        'recipient_user_id': notification.recipient_user_id,
                        'message': notification.message,
                        'type': notification.type,
                        'read_at': notification.read_at.isoformat() if notification.read_at else None,
                        'created_at': notification.created_at.isoformat(),
                    }
                }
            )
            logger.info(f"✓ Sent WebSocket notification to user {recipient_user_id}")
        except Exception as ws_error:
            logger.error(f"Failed to send WebSocket notification: {ws_error}")
            # Don't fail the whole process if WebSocket fails
        
        # Acknowledge the message
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info(f"✓ Acknowledged message {method.delivery_tag}")
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}")
        ch.basic_ack(delivery_tag=method.delivery_tag)  # Acknowledge to remove from queue
    except Exception as e:
        logger.error(f"Error processing notification event: {e}", exc_info=True)
        # Negative acknowledgment - message will be requeued
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def start_consumer():
    """
    Start the RabbitMQ consumer
    """
    logger.info("🚀 Starting RabbitMQ Notification Consumer...")
    
    while True:
        try:
            # Connect to RabbitMQ
            connection = get_rabbitmq_connection()
            channel = connection.channel()
            
            # Declare the queue (idempotent - safe to call multiple times)
            channel.queue_declare(
                queue=QUEUE_NAME,
                durable=True,  # Survive broker restart
                arguments={
                    'x-message-ttl': 86400000,  # 24 hours TTL for messages
                    'x-max-length': 10000,  # Maximum 10k messages in queue
                }
            )
            
            # Set QoS - process one message at a time
            channel.basic_qos(prefetch_count=1)
            
            logger.info(f"✓ Listening on queue: {QUEUE_NAME}")
            logger.info("⏳ Waiting for notification events...")
            
            # Start consuming
            channel.basic_consume(
                queue=QUEUE_NAME,
                on_message_callback=process_notification_event,
                auto_ack=False  # Manual acknowledgment
            )
            
            channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("🛑 Consumer stopped by user")
            break
        except Exception as e:
            logger.error(f"Consumer error: {e}", exc_info=True)
            logger.info("Reconnecting in 5 seconds...")
            time.sleep(5)


if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    start_consumer()
