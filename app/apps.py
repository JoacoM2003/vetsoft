from django.apps import AppConfig


class AppConfig(AppConfig):
    """Esta clase configura los ajustes predeterminados para la aplicación 'app'"""
    
    default_auto_field = "django.db.models.BigAutoField"
    name = "app"
