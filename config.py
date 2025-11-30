import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings configuration"""
    
    # Green API Configuration (optional - can be set via localStorage)
    green_api_url: str = "https://api.green-api.com"
    green_api_id_instance: Optional[str] = None
    green_api_token_instance: Optional[str] = None
    
    # User Configuration
    user_phone_number: Optional[str] = None
    
    # OpenRouter Configuration (optional - can be set via localStorage)
    openrouter_api_key: Optional[str] = None
    openrouter_model: str = "openai/gpt-4o"
    
    # Application Configuration
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = True
    
    # Database Configuration
    database_url: str = "sqlite:///./whatsapp_bot.db"
    
    # Message Processing Configuration
    max_messages_per_chat: int = 4
    message_analysis_minutes: int = 1440  # 24 hours default
    analyze_group_chats: bool = False
    analyze_all_conversations: bool = False
    
    # Cron Schedule Configuration
    cron_enabled: bool = False
    cron_schedule: str = "0 9 * * *"  # Default: 9 AM daily (cron format)

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
