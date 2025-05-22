import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from asgiref.sync import sync_to_async
from .models import ChatRoom, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"

        user = self.scope["user"]
        if user is None or isinstance(user, AnonymousUser):
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        history = await self._get_history(limit=30)  # 오래된 순
        await self.send(text_data=json.dumps({
            "type": "chat_history",
            "messages": history,
        }))

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg = await self._save_message(data["message"])
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "chat_message", "id": msg.id, "sender": msg.sender.username, "text": msg.text, "sent_at": msg.sent_at.isoformat()},
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @sync_to_async
    def _save_message(self, text):
        from .models import ChatRoom
        msg = Message.objects.create(
            room_id=self.room_id,
            sender=self.scope["user"],
            text=text,
        )
        # updated_at 갱신
        ChatRoom.objects.filter(id=self.room_id).update(updated_at=msg.sent_at)
        return msg

    @sync_to_async
    def _get_history(self, limit=30):
        qs = (Message.objects
              .filter(room_id=self.room_id)
              .select_related("sender")
              .order_by("-sent_at")[:limit][::-1])  # 오래된 것부터
        return [
            {"id": m.id, "sender": m.sender.username, "text": m.text,
             "sent_at": m.sent_at.isoformat()}
            for m in qs
        ]