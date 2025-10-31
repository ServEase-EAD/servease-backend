#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting Notification Service..."

# Change to app directory
cd /app

# Run migrations
echo "📦 Running database migrations..."
python manage.py migrate --noinput

# Start Daphne in the background
echo "🌐 Starting Daphne ASGI server on port 8006..."
daphne -b 0.0.0.0 -p 8006 notification_service.asgi:application &
DAPHNE_PID=$!

# Wait a moment for Daphne to start
sleep 2

# Start RabbitMQ consumer in the background
echo "🐰 Starting RabbitMQ consumer..."
cd /app && python -m app_notifications.rabbitmq_consumer &
CONSUMER_PID=$!

# Function to handle shutdown
shutdown() {
    echo "🛑 Shutting down services..."
    kill $DAPHNE_PID $CONSUMER_PID 2>/dev/null
    wait $DAPHNE_PID $CONSUMER_PID 2>/dev/null
    echo "✓ Services stopped"
    exit 0
}

# Trap termination signals
trap shutdown SIGTERM SIGINT

echo "✓ All services started successfully"
echo "  - Daphne (PID: $DAPHNE_PID)"
echo "  - RabbitMQ Consumer (PID: $CONSUMER_PID)"
echo "⏳ Services running..."

# Wait for processes
wait
