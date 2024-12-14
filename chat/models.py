from django.db import models
from django.contrib.auth.models import User

class Discussion(models.Model):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="discussions")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class Message(models.Model):
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name="messages")
    sender = models.CharField(max_length=50)  # 'user' or 'AI'
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} at {self.created_at}"
