from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Task Management System'
    
    def ready(self):
        # Import signal handlers
        import core.signals
