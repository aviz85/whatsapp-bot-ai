"""
Middleware to inject localStorage config into requests
"""
from fastapi import Request
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ConfigInjector:
    """Injects configuration from request body into settings"""
    
    @staticmethod
    def extract_config(request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract config from request body
        
        Args:
            request_data: Request body dictionary
            
        Returns:
            Configuration dictionary or None
        """
        return request_data.get('config')
    
    @staticmethod
    def apply_config(config: Dict[str, Any]):
        """
        Apply configuration to settings temporarily
        
        Args:
            config: Configuration dictionary
        """
        from config import settings
        from green_api_client import GreenAPIClient
        from openrouter_client import OpenRouterClient
        
        if not config:
            return
        
        # Update settings temporarily (in-memory only)
        if config.get('green_api_url'):
            settings.green_api_url = config['green_api_url']
        
        if config.get('green_api_id'):
            settings.green_api_id_instance = config['green_api_id']
        
        if config.get('green_api_token'):
            settings.green_api_token_instance = config['green_api_token']
        
        if config.get('user_phone_number'):
            settings.user_phone_number = config['user_phone_number']
        
        if config.get('openrouter_key'):
            settings.openrouter_api_key = config['openrouter_key']
        
        if config.get('ai_model'):
            settings.openrouter_model = config['ai_model']
        
        logger.info("Configuration applied from request")
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate configuration
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not config:
            return False, "No configuration provided"
        
        # Check required fields
        required_fields = ['green_api_id', 'green_api_token', 'openrouter_key']
        missing_fields = [field for field in required_fields if not config.get(field)]
        
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        return True, ""


# Global instance
config_injector = ConfigInjector()
