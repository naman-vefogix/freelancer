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
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    bio = models.TextField(blank=True, max_length=255)
    skills = models.CharField(max_length=255, blank= True)


