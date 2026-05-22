from django.contrib import admin
from .models import Notification

# Register your models here.

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id','user','title','is_read','created_at')
    list_filter = ('is_read','created_at')
    search_fields = ('user__username','title','messages')
