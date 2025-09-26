"""
Customer Service App Configuration
"""

from django.apps import AppConfig


class CustomersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'customers'
    verbose_name = 'Customer Management'

    def ready(self):
        """
        Initialize app-specific configurations when Django starts
        """
        # Import signal handlers if needed
        # import customers.signals
