#!/bin/bash

set -euo pipefail

log() {
    printf '[notification-service] %s\n' "$@"
}

log "Starting service bootstrap"

cd /app

log "Applying database migrations"
python manage.py migrate

log "Starting Daphne on port 8006"
daphne -b 0.0.0.0 -p 8006 notification_service.asgi:application &
DAPHNE_PID=$!

sleep 2

log "Starting RabbitMQ consumer"
python -m app_notifications.rabbitmq_consumer &
CONSUMER_PID=$!

shutdown() {
    log "Stopping background processes"
    kill "$DAPHNE_PID" "$CONSUMER_PID" 2>/dev/null || true
    wait "$DAPHNE_PID" "$CONSUMER_PID" 2>/dev/null || true
    log "Shutdown complete"
    exit 0
}

trap shutdown SIGTERM SIGINT

log "Service started (Daphne PID=$DAPHNE_PID, Consumer PID=$CONSUMER_PID)"

wait "$DAPHNE_PID" "$CONSUMER_PID"
