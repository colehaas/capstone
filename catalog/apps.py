from django.apps import AppConfig


class CatalogConfig(AppConfig):
    name = 'catalog'
    def ready(self):
        from scheduler import scheduler
        scheduler.start()