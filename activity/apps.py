from django.apps import AppConfig

class ActivityConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'activity'
    def ready(self):
        from .scheduler import start_scheduler
        from .signals import register_all
        register_all()
        start_scheduler()