from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'products'

    def ready(self):
        """Démarre le consumer RabbitMQ quand l'app est prête"""
        import os
        if os.environ.get('RUN_MAIN', None) != 'true':
            from .service_product import start_consumer_thread
            start_consumer_thread()
