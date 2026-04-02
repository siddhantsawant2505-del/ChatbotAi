from django.db import models
from django.utils.timezone import now

# Create your models here.
class ChatSession(models.Model):
    session_data = models.JSONField()  # Stores chat as JSON
    timestamp = models.DateTimeField(default=now)


class Chat(models.Model):
    user_input = models.TextField()
    ai_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat at {self.created_at}"
