from django.conf import settings
from django.db import models

class ChatRoom(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chats_as_user1")
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chats_as_user2")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user1", "user2")  # 같은 조합 방 하나만

    @staticmethod
    def get_room(u1, u2):
        if u1.id > u2.id:
            u1, u2 = u2, u1
        room, _ = ChatRoom.objects.get_or_create(user1=u1, user2=u2)
        return room

class Message(models.Model):
    room   = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text   = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # 메시지 저장될 때 방의 updated_at 갱신
        self.room.save(update_fields=["updated_at"])