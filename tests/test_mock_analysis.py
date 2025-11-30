import asyncio
import logging
import sys
import os
from unittest.mock import MagicMock
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import GreenAPIMessage, PriorityReport
from whatsapp_bot import WhatsAppBot
from config import settings

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_test():
    logger.info("Starting Mock Analysis Test")
    
    # Initialize bot
    bot = WhatsAppBot()
    
    # Mock Green API Client
    bot.green_client = MagicMock()
    
    # Mock incoming messages (3 chats)
    now = int(datetime.now().timestamp())
    
    incoming_messages = [
        GreenAPIMessage(
            id_message="msg1", chat_id="123@c.us", type="incoming", 
            timestamp=now, type_message="textMessage", text_message="Hello",
            sender_id="123@c.us", sender_name="User 1"
        ),
        GreenAPIMessage(
            id_message="msg2", chat_id="456@c.us", type="incoming", 
            timestamp=now, type_message="textMessage", text_message="Hi",
            sender_id="456@c.us", sender_name="User 2"
        ),
        GreenAPIMessage(
            id_message="msg3", chat_id="789@g.us", type="incoming", 
            timestamp=now, type_message="textMessage", text_message="Group msg",
            sender_id="999@c.us", sender_name="User 3"
        )
    ]
    
    bot.green_client.get_last_incoming_messages.return_value = incoming_messages
    
    # Mock Chat History
    # Chat 1: Last message is incoming (Unanswered)
    chat1_history = [
        GreenAPIMessage(
            id_message="msg1", chat_id="123@c.us", type="incoming", 
            timestamp=now, type_message="textMessage", text_message="Hello",
            sender_id="123@c.us", sender_name="User 1"
        )
    ]
    
    # Chat 2: Last message is outgoing (Answered)
    chat2_history = [
        GreenAPIMessage(
            id_message="reply1", chat_id="456@c.us", type="outgoing", 
            timestamp=now+10, type_message="textMessage", text_message="My reply",
            sender_id="me", sender_name="Me"
        ),
        GreenAPIMessage(
            id_message="msg2", chat_id="456@c.us", type="incoming", 
            timestamp=now, type_message="textMessage", text_message="Hi",
            sender_id="456@c.us", sender_name="User 2"
        )
    ]
    
    # Chat 3: Group chat (Unanswered)
    chat3_history = [
        GreenAPIMessage(
            id_message="msg3", chat_id="789@g.us", type="incoming", 
            timestamp=now, type_message="textMessage", text_message="Group msg",
            sender_id="999@c.us", sender_name="User 3"
        )
    ]
    
    def get_history_side_effect(chat_id, count=10):
        if chat_id == "123@c.us": return chat1_history
        if chat_id == "456@c.us": return chat2_history
        if chat_id == "789@g.us": return chat3_history
        return []
        
    bot.green_client.get_chat_history.side_effect = get_history_side_effect
    
    # Mock OpenRouter Client
    bot.openrouter_client = MagicMock()
    bot.openrouter_client.analyze_conversations.return_value = PriorityReport(
        urgent_conversations=[], important_conversations=[], normal_conversations=[],
        summary="Test Summary", total_conversations=1
    )
    bot.openrouter_client.generate_summary_report.return_value = "Mock Report"
    
    # Mock Send Message
    bot.green_client.send_message.return_value = {"idMessage": "sent123"}
    
    # --- Test Case 1: Default Settings (No Groups, Only Open) ---
    logger.info("\n=== Test Case 1: Default Settings (No Groups, Only Open) ===")
    settings.analyze_group_chats = False
    settings.analyze_all_conversations = False
    
    # We need to spy on message_analyzer.analyze_conversations to see what it received
    # But it's easier to check the logs or the result if we mock the analyzer
    # Let's just run it and check the logs (which will be printed)
    
    await bot.analyze_and_report_with_progress(minutes=60)
    
    # --- Test Case 2: Include Groups ---
    logger.info("\n=== Test Case 2: Include Groups ===")
    settings.analyze_group_chats = True
    settings.analyze_all_conversations = False
    
    await bot.analyze_and_report_with_progress(minutes=60)
    
    # --- Test Case 3: Analyze All ---
    logger.info("\n=== Test Case 3: Analyze All ===")
    settings.analyze_group_chats = True
    settings.analyze_all_conversations = True
    
    await bot.analyze_and_report_with_progress(minutes=60)
    
    logger.info("\nTest Completed Successfully")

if __name__ == "__main__":
    asyncio.run(run_test())
