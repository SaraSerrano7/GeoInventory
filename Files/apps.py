"""
Django auto configuration for Files app
"""

from django.apps import AppConfig


class FilesConfig(AppConfig):
    """
    Main config
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Files'
