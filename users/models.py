from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('client','Client'),
        ('freelancer', 'freelancer'),
    )
    role = models.CharField(max_length = 20, choices = ROLE_CHOICES)
    is_verified = models.BooleanField(default=False)

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, max_length=255)
    skills = models.CharField(max_length=255, blank= True)


class UserActivity(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=50)
    action_type = models.CharField(max_length=50, null= True, blank= True)
    entity_name = models.CharField(max_length=50, null= True, blank= True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta : 
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["event_type"]),
            models.Index(fields=["created_at"]),
        ]