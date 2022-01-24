"""
This module contains our configuration settings for the "accounts" application.
"""
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """
    The AccountsConfig object stores the configuration for the "accounts" application
    """
    # Override the name of the application in AppConfig
    name = 'accounts'
