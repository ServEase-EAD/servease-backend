import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    """
    Handles real-time WebSocket communication for user notifications.
    """
    async def connect(self):
        # Get the user ID from the URL route
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        # Create a channel group name specific to the user
        self.user_group_name = f'notifications_{self.user_id}'

        # Join the user's group. This allows the background tasks 
        # (like when a new appointment is created) to send messages here.
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        await self.accept()
        print(f"WebSocket Connected for User: {self.user_id}")
        
        # Optionally send a confirmation message
        await self.send(text_data=json.dumps({
            'status': 'connected',
            'message': f'Ready to receive notifications for user {self.user_id}'
        }))

    async def disconnect(self, close_code):
        # Leave the user's group
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )
        print(f"WebSocket Disconnected for User: {self.user_id}")

    # Receive message from WebSocket (client side)
    async def receive(self, text_data):
        """Handle incoming messages from the client (e.g., 'mark as read')"""
        text_data_json = json.loads(text_data)
        command = text_data_json.get('command')

        # Simple example of handling a command from the client
        if command == 'ping':
            await self.send(text_data=json.dumps({'command': 'pong'}))

    # Receive message from channel group (server side)
    async def send_notification(self, event):
        """Handler for messages sent to the user's group by the server"""
        
        # Send the event's data payload to the WebSocket
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'new_notification',
            'data': message
        }))
        
        print(f"Sent notification to User {self.user_id}")