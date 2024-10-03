
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.room_group_name = f"user_{self.user.id}_notifications"

        # গ্রুপে যোগ দিন
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # গ্রুপ থেকে বের হন
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # ক্লায়েন্ট থেকে মেসেজ পেলে কী করবেন
        pass

    async def send_notification(self, event):
        # নোটিফিকেশন পাঠান
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification']
        }))

