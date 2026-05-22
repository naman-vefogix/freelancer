from django.db import models
from users.models import CustomUser
# Create your models here.

class Notification(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    user  = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} -> {self.title}"