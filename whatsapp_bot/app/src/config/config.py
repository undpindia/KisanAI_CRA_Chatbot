from pydantic_settings import BaseSettings
import logging
import os
from pathlib import Path
from functools import lru_cache

def clear_environment_variables():
    """Clear all relevant environment variables except OPENAI_API_KEY"""
    env_vars = [
        'WHATSAPP_ACCESS_TOKEN',
        'WHATSAPP_NUMBER_ID',
        'WHATSAPP_HOOK_TOKEN',
        'APP_URL',
        'DATABASE_URL',
        'MONGO_DB_NAME',
        'MONGO_DB_USER_COLLECTION',
        'MONGO_DB_CONVERSATION_COLLECTION',
        'AZURE_SPEECH_SUBSCRIPTION_KEY',
        'AZURE_SPEECH_REGION',
        'AZURE_TRANSLATOR_KEY',
        'AZURE_TRANSLATOR_REGION',
        'AZURE_TRANSLATOR_ENDPOINT',
        'SENTRY_DSN'
    ]
    for var in env_vars:
        if var in os.environ:
            os.environ.pop(var)

def set_openai_key(api_key: str):
    """Set OpenAI API key in environment"""
    os.environ['OPENAI_API_KEY'] = api_key

def reload_settings():
    """Force reload settings by clearing cache and environment"""
    clear_environment_variables()
    get_settings.cache_clear()
    settings = get_settings()
    set_openai_key(settings.OPENAI_API_KEY)
    return settings

class Settings(BaseSettings):
    DATABASE_URL: str
    MONGO_DB_NAME: str
    MONGO_DB_USER_COLLECTION: str
    MONGO_DB_CONVERSATION_COLLECTION: str
    WHATSAPP_ACCESS_TOKEN: str
    WHATSAPP_NUMBER_ID: str
    WHATSAPP_HOOK_TOKEN: str
    OPENAI_API_KEY: str
    APP_URL: str
    AZURE_SPEECH_SUBSCRIPTION_KEY: str
    AZURE_SPEECH_REGION: str
    AZURE_TRANSLATOR_KEY: str
    AZURE_TRANSLATOR_REGION: str
    AZURE_TRANSLATOR_ENDPOINT: str
    SENTRY_DSN: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = True
        extra = 'ignore'

    def __init__(self, **kwargs):
        clear_environment_variables()
        super().__init__(**kwargs)
        set_openai_key(self.OPENAI_API_KEY)

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = reload_settings()
