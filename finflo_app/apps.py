from django.apps import AppConfig
# Configure context processors file
class FinfloAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "finflo_app"

    def ready(self):
        import finflo_app.context_processors  
