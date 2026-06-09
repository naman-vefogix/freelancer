from django.db import models

# Create your models here.

class UserActivity(models.Model):
    user_id = models.IntegerField(null=True, blank=True, db_index=True)
    event_type = models.CharField(max_length=50)
    action_type = models.CharField(max_length=50, null=True, blank=True)
    entity_name = models.CharField(max_length=50, null=True, blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'activity'  
        indexes = [
            models.Index(fields=["user_id"]),
            models.Index(fields=["event_type"]),
            models.Index(fields=["created_at"]),
        ]