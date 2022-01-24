"""
This module contains our configuration settings for the "core" application.
"""
from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    The CoreConfig object stores the configuration for the "core" application
    """
    # Override the name of the application in AppConfig
    name = 'core'
