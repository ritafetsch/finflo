from django.apps import AppConfig
from django.db.models.signals import post_migrate

def create_default_currencies(sender, **kwargs):
    from .models import Currency
    
    currencies_data = [
        {'name': 'British Pound', 'code': 'GBP', 'symbol': '£', 'exchange_rate': 0.7180},  # Listed first to make it the default
        {'name': 'Euro', 'code': 'EUR', 'symbol': '€', 'exchange_rate': 0.8500},
        {'name': 'US Dollar', 'code': 'USD', 'symbol': '$', 'exchange_rate': 1.0000},
        {'name': 'Japanese Yen', 'code': 'JPY', 'symbol': '¥', 'exchange_rate': 110.8800},
        {'name': 'Canadian Dollar', 'code': 'CAD', 'symbol': '$', 'exchange_rate': 1.2500},
        {'name': 'Swiss Franc', 'code': 'CHF', 'symbol': 'CHF', 'exchange_rate': 0.9170},
        {'name': 'Australian Dollar', 'code': 'AUD', 'symbol': '$', 'exchange_rate': 1.3450},
        {'name': 'Chinese Yuan Renminbi', 'code': 'CNY', 'symbol': '¥', 'exchange_rate': 6.4540},
        {'name': 'Indian Rupee', 'code': 'INR', 'symbol': '₹', 'exchange_rate': 73.0400},
        {'name': 'Brazilian Real', 'code': 'BRL', 'symbol': 'R$', 'exchange_rate': 5.2500},
        {'name': 'South Korean Won', 'code': 'KRW', 'symbol': '₩', 'exchange_rate': 1190.00},
        {'name': 'Mexican Peso', 'code': 'MXN', 'symbol': '$', 'exchange_rate': 19.8000},
        {'name': 'Singapore Dollar', 'code': 'SGD', 'symbol': '$', 'exchange_rate': 1.3600},
        {'name': 'Hong Kong Dollar', 'code': 'HKD', 'symbol': '$', 'exchange_rate': 7.7800},
        {'name': 'Russian Ruble', 'code': 'RUB', 'symbol': '₽', 'exchange_rate': 76.8500},
        {'name': 'South African Rand', 'code': 'ZAR', 'symbol': 'R', 'exchange_rate': 15.4500},
        {'name': 'New Zealand Dollar', 'code': 'NZD', 'symbol': '$', 'exchange_rate': 1.4300},
        {'name': 'Swedish Krona', 'code': 'SEK', 'symbol': 'kr', 'exchange_rate': 8.5500},
        {'name': 'Norwegian Krone', 'code': 'NOK', 'symbol': 'kr', 'exchange_rate': 8.9500},
        {'name': 'Danish Krone', 'code': 'DKK', 'symbol': 'kr', 'exchange_rate': 6.2700},
    ]
    
    # Ensure GBP is currency_id=1 (as the default currency)
    if not Currency.objects.filter(currency_id=1).exists():
        gbp_data = next((c for c in currencies_data if c['code'] == 'GBP'), None)
        if gbp_data:
            Currency.objects.create(
                currency_id=1,
                **gbp_data
            )
            print("Created GBP as the default currency with ID 1")
    
    # Create all other currencies
    for currency_data in currencies_data:
        code = currency_data['code']
        if code != 'GBP' or not Currency.objects.filter(code='GBP').exists():
            Currency.objects.get_or_create(
                code=code,
                defaults=currency_data
            )

def create_default_categories(sender, **kwargs):
    from .models import Category
    if not Category.objects.filter(is_default=True).exists():
        defaults = [
            {'name': 'Groceries', 'color': '#FF5733', 'is_default': True},
            {'name': 'Entertainment', 'color': '#66CCFF', 'is_default': True},
            {'name': 'Utilities', 'color': '#FFC300', 'is_default': True},
            {'name': 'Dining Out', 'color': '#FF5733', 'is_default': True},
            {'name': 'Transportation', 'color': '#E71D36', 'is_default': True},
            {'name': 'Clothing', 'color': '#F4A261', 'is_default': True},
            {'name': 'Gifts', 'color': '#2EC4B6', 'is_default': True},
            {'name': 'Household Items', 'color': '#006D77', 'is_default': True},
            {'name': 'Random', 'color': '#FF00FF', 'is_default': True},
            {'name': 'Travel', 'color': '#00BFFF', 'is_default': True},
            {'name': 'Hobbies', 'color': '#00FF00', 'is_default': True},
            {'name': 'Fitness', 'color': '#FFD700', 'is_default': True},
            {'name': 'Pets', 'color': '#228B22', 'is_default': True},
            {'name': 'Beauty', 'color': '#FF1493', 'is_default': True},
            {'name': 'Sports', 'color': '#800080', 'is_default': True},
            {'name': 'Other', 'color': '#FFF094', 'is_default': True},
            {'name': 'Work', 'color': '#0003FF', 'is_default': True},
        ]
        for default in defaults:
            Category.objects.get_or_create(
                name=default['name'], 
                defaults={'color': default['color'], 'is_default': default['is_default']}
            )

# Configure context processors file
class FinfloAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "finflo_app"

    def ready(self):
        import finflo_app.context_processors  
        post_migrate.connect(create_default_currencies, sender=self)
        post_migrate.connect(create_default_categories, sender=self)