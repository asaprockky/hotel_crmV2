from django.apps import AppConfig

class MainPageConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.home'  # Ensure this matches `INSTALLED_APPS`
