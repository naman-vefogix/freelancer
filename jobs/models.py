from django.db import models
from users.models import CustomUser

# Create your models here.

class Job(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField()
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="jobs")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) :
        return self.title
    
class Applications(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    freelancer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="applications")
    cover_letter = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.freelancer.username} -> {self.job.title}"
    