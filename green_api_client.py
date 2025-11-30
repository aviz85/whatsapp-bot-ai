import requests
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from config import settings
from models import GreenAPIMessage


class GreenAPIClient:
    """Client for interacting with Green API"""
    
    def __init__(self):
        self.base_url = settings.green_api_url
        self.id_instance = settings.green_api_id_instance
        self.token_instance = settings.green_api_token_instance
        self.logger = logging.getLogger(__name__)
    
    def _make_request(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to Green API"""
        url = f"{self.base_url}/waInstance{self.id_instance}/{endpoint}/{self.token_instance}"
        
        try:
            if method == "GET":
                response = requests.get(url)
            elif method == "POST":
                response = requests.post(url, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Green API request failed: {e}")
            raise
    
    def get_last_incoming_messages(self, minutes: int = 1440) -> List[GreenAPIMessage]:
        """
        Get last incoming messages from Green API
        
        Args:
            minutes: Time period in minutes to fetch messages (default: 1440 = 24 hours)
        
        Returns:
            List of GreenAPIMessage objects
        """
        try:
            endpoint = f"lastIncomingMessages/{self.token_instance}"
            url = f"{self.base_url}/waInstance{self.id_instance}/{endpoint}?minutes={minutes}"
            
            self.logger.info(f"Fetching messages from Green API for the last {minutes} minutes")
            response = requests.get(url)
            response.raise_for_status()
            
            messages_data = response.json()
            messages = []
            
            for msg_data in messages_data:
                # Convert snake_case to camelCase for our model
                message = GreenAPIMessage(
                    type=msg_data.get('type', ''),
                    id_message=msg_data.get('idMessage', ''),
                    timestamp=msg_data.get('timestamp', 0),
                    type_message=msg_data.get('typeMessage', ''),
                    chat_id=msg_data.get('chatId', ''),
                    sender_id=msg_data.get('senderId'),
                    sender_name=msg_data.get('senderName'),
                    sender_contact_name=msg_data.get('senderContactName'),
                    text_message=msg_data.get('textMessage'),
                    is_forwarded=msg_data.get('isForwarded', False),
                    forwarding_score=msg_data.get('forwardingScore', 0),
                    download_url=msg_data.get('downloadUrl'),
                    caption=msg_data.get('caption'),
                    file_name=msg_data.get('fileName'),
                    is_edited=msg_data.get('isEdited', False),
                    is_deleted=msg_data.get('isDeleted', False)
                )
                messages.append(message)
            
            self.logger.info(f"Successfully fetched {len(messages)} messages")
            return messages
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch messages from Green API: {e}")
            raise
    
    def send_message(self, chat_id: str, message: str) -> Dict[str, Any]:
        """
        Send a message via Green API
        
        Args:
            chat_id: Target chat ID
            message: Message content
        
        Returns:
            Response from Green API
        """
        try:
            endpoint = f"sendMessage/{self.token_instance}"
            url = f"{self.base_url}/waInstance{self.id_instance}/{endpoint}"
            
            data = {
                "chatId": chat_id,
                "message": message
            }
            
            self.logger.info(f"Sending message to chat {chat_id}")
            response = requests.post(url, json=data)
            response.raise_for_status()
            
            result = response.json()
            self.logger.info(f"Message sent successfully with ID: {result.get('idMessage')}")
            return result
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to send message via Green API: {e}")
            raise
    
    
    # Cache for connection status to avoid hitting rate limits
    _connection_cache = {
        'timestamp': 0,
        'status': False,
        'message': ''
    }
    _cache_duration = 60  # seconds

    def verify_connection(self, force_refresh: bool = False) -> tuple[bool, str]:
        """
        Verify connection to Green API
        
        Args:
            force_refresh: If True, ignore cache and force a new check
            
        Returns:
            Tuple of (is_connected: bool, message: str)
        """
        import time
        
        # Check cache
        if not force_refresh:
            current_time = time.time()
            if current_time - self._connection_cache['timestamp'] < self._cache_duration:
                return self._connection_cache['status'], self._connection_cache['message']

        try:
            # Check if credentials are configured
            if not self.id_instance or not self.token_instance:
                # Update cache for this specific failure
                self._connection_cache = {
                    'timestamp': time.time(),
                    'status': False,
                    'message': "Green API credentials not configured"
                }
                return False, "Green API credentials not configured"
            
            # Try to get account settings as a connectivity test
            endpoint = f"getStateInstance/{self.token_instance}"
            url = f"{self.base_url}/waInstance{self.id_instance}/{endpoint}"
            
            response = requests.get(url, timeout=10)
            
            # Handle 429 specifically
            if response.status_code == 429:
                self.logger.warning("Green API rate limit reached (429)")
                # If we have a cached status (even if expired), return it with a warning
                if self._connection_cache['timestamp'] > 0:
                    return self._connection_cache['status'], f"{self._connection_cache['message']} (Cached - Rate Limit)"
                
                # Update cache for rate limit
                self._connection_cache = {
                    'timestamp': time.time(),
                    'status': False,
                    'message': "Rate limit reached. Please wait."
                }
                return False, "Rate limit reached. Please wait."

            response.raise_for_status()
            
            result = response.json()
            
            state = result.get('stateInstance')
            
            if state == 'authorized':
                status, msg = True, "Connected and authorized"
            elif state == 'notAuthorized':
                status, msg = False, "WhatsApp not authorized. Please scan QR code."
            elif state == 'blocked':
                status, msg = False, "Instance is blocked"
            elif state == 'sleepMode':
                status, msg = False, "Instance is in sleep mode"
            elif state == 'starting':
                status, msg = False, "Instance is starting..."
            else:
                status, msg = False, f"Unknown state: {state}"
                
            # Update cache
            self._connection_cache = {
                'timestamp': time.time(),
                'status': status,
                'message': msg
            }
            self.logger.info(f"Green API connection verified successfully: {msg}")
            return status, msg
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to verify Green API connection: {e}")
            return False, f"HTTP error: {e.response.status_code if hasattr(e, 'response') else 'Unknown'}"
        except Exception as e:
            self.logger.error(f"Error verifying connection: {e}")
            return False, f"Error: {str(e)}"
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get account information from Green API"""
        try:
            endpoint = f"getWaSettings/{self.token_instance}"
            url = f"{self.base_url}/waInstance{self.id_instance}/{endpoint}"
            
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get account info from Green API: {e}")
            raise

    def get_chat_history(self, chat_id: str, count: int = 10) -> List[GreenAPIMessage]:
        """
        Fetch chat history for a specific chat
        
        Args:
            chat_id: Chat ID to fetch history for
            count: Number of messages to fetch
            
        Returns:
            List of GreenAPIMessage objects
        """
        try:
            endpoint = f"getChatHistory/{self.token_instance}"
            url = f"{self.base_url}/waInstance{self.id_instance}/{endpoint}"
            
            payload = {
                "chatId": chat_id,
                "count": count
            }
            
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            messages_data = response.json()
            messages = []
            
            for msg_data in messages_data:
                # Convert snake_case to camelCase for our model
                message = GreenAPIMessage(
                    type=msg_data.get('type', ''),
                    id_message=msg_data.get('idMessage', ''),
                    timestamp=msg_data.get('timestamp', 0),
                    type_message=msg_data.get('typeMessage', ''),
                    chat_id=msg_data.get('chatId', ''),
                    sender_id=msg_data.get('senderId'),
                    sender_name=msg_data.get('senderName'),
                    sender_contact_name=msg_data.get('senderContactName'),
                    text_message=msg_data.get('textMessage'),
                    is_forwarded=msg_data.get('isForwarded', False),
                    forwarding_score=msg_data.get('forwardingScore', 0),
                    download_url=msg_data.get('downloadUrl'),
                    caption=msg_data.get('caption'),
                    file_name=msg_data.get('fileName'),
                    is_edited=msg_data.get('isEdited', False),
                    is_deleted=msg_data.get('isDeleted', False)
                )
                messages.append(message)
            
            # Reverse to have oldest first
            messages.reverse()
            return messages
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch chat history for {chat_id}: {e}")
            # Return empty list on error to allow continuing
            return []

