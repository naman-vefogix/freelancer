from django.contrib import admin
from .models import Job, Applications

# Register your models here.

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'created_at')
    search_fields = ('title', 'client__username')

@admin.register(Applications)
class ApplicationsAdmin(admin.ModelAdmin):
    list_display = ('job', 'freelancer', "applied_at")
    search_fields = ('job__title', 'freelancer__username')

