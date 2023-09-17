# SCRIPT TO POPULATE CURRENCIES IN DATABASE

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finflo_project.settings')
django.setup()

from finflo_app.models import Currency
def run():
    currencies_data = [
        {'name': 'Euro', 'code': 'EUR', 'symbol': '€', 'exchange_rate': 0.8500},
        {'name': 'US Dollar', 'code': 'USD', 'symbol': '$', 'exchange_rate': 1.0000},
        {'name': 'Japanese Yen', 'code': 'JPY', 'symbol': '¥', 'exchange_rate': 110.8800},
        {'name': 'British Pound', 'code': 'GBP', 'symbol': '£', 'exchange_rate': 0.7180},
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

    for currency_data in currencies_data:
        currency, created = Currency.objects.get_or_create(
            code=currency_data['code'],
            defaults=currency_data
        )
        if created:
            print(f"Currency '{currency.name}' created.")
        else:
            print(f"Currency '{currency.name}' already exists.")
