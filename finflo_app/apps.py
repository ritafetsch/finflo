from django.apps import AppConfig
from django.db.models.signals import post_migrate

def create_default_currencies(sender, **kwargs):
    from .models import Currency
    if not Currency.objects.exists():
        Currency.objects.create(
            name='US Dollar',
            code='USD',
            symbol='$',
            exchange_rate=1.0
        )
# Configure context processors file
class FinfloAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "finflo_app"

    def ready(self):
        import finflo_app.context_processors  
