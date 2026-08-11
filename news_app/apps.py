from django.apps import AppConfig


class NewsAppConfig(AppConfig):
    """Application configuration for news_app[cite: 12]."""
    
    name = 'news_app'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        """Import signals module upon application initialization[cite: 12]."""
        import news_app.signals
