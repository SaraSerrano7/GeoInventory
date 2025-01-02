"""
Api's app configuration
"""
from django.apps import AppConfig


class ApiConfig(AppConfig):
    """
    API's main config
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Api'
