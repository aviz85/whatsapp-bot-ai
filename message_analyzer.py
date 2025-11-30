import logging
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from models import GreenAPIMessage, ChatConversation
from config import settings


class MessageAnalyzer:
    """Analyzes WhatsApp messages to identify open conversations and prioritize them"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.max_messages_per_chat = settings.max_messages_per_chat
    
    def group_messages_by_chat(self, messages: List[GreenAPIMessage]) -> List[ChatConversation]:
        """
        Group messages by chat ID and create conversation objects
        
        Args:
            messages: List of messages to group
        
        Returns:
            List of ChatConversation objects
        """
        chat_groups = defaultdict(list)
        
        # Group messages by chat_id
        for message in messages:
            chat_groups[message.chat_id].append(message)
        
        conversations = []
        
        # Create conversation objects for each chat
        for chat_id, chat_messages in chat_groups.items():
            # Sort messages by timestamp (oldest first)
            chat_messages.sort(key=lambda x: x.timestamp)
            
            # Get the last N messages for analysis
            recent_messages = chat_messages[-self.max_messages_per_chat:]
            
            # Extract chat name from the most recent message
            chat_name = None
            if recent_messages:
                last_msg = recent_messages[-1]
                chat_name = last_msg.sender_contact_name or last_msg.sender_name
            
            conversation = ChatConversation(
                chat_id=chat_id,
                chat_name=chat_name,
                messages=recent_messages,
                last_message_time=recent_messages[-1].datetime if recent_messages else datetime.now(),
                is_unanswered=self._is_conversation_unanswered(recent_messages)
            )
            
            conversations.append(conversation)
        
        # Sort conversations by last message time (most recent first)
        conversations.sort(key=lambda x: x.last_message_time, reverse=True)
        
        self.logger.info(f"Grouped {len(messages)} messages into {len(conversations)} conversations")
        return conversations
    
    def _is_conversation_unanswered(self, messages: List[GreenAPIMessage]) -> bool:
        """
        Determine if a conversation is unanswered (open)
        
        A conversation is considered unanswered if:
        1. The last message is from someone else (not from me)
        2. I haven't sent a message after their last message
        
        Args:
            messages: List of messages in chronological order
        
        Returns:
            True if conversation is unanswered, False otherwise
        """
        if not messages:
            return False
        
        # Get the last message
        last_message = messages[-1]
        
        # If the last message is incoming (from someone else), it's unanswered
        if last_message.type == "incoming":
            return True
        
        # If the last message is outgoing (from me), check if there was an incoming message after my last outgoing
        # This is a more complex scenario - for now, we'll consider it answered
        return False
    
    def identify_open_conversations(self, conversations: List[ChatConversation]) -> List[ChatConversation]:
        """
        Filter and return only open (unanswered) conversations
        
        Args:
            conversations: List of all conversations
        
        Returns:
            List of unanswered conversations
        """
        open_conversations = [conv for conv in conversations if conv.is_unanswered]
        
        self.logger.info(f"Found {len(open_conversations)} open conversations out of {len(conversations)} total")
        return open_conversations
    
    def get_conversation_summary(self, conversation: ChatConversation) -> Dict:
        """
        Create a summary of a conversation for AI analysis
        
        Args:
            conversation: ChatConversation to summarize
        
        Returns:
            Dictionary with conversation summary
        """
        messages_text = []
        
        for i, msg in enumerate(conversation.messages):
            sender = "את/ה" if msg.type == "incoming" else "אני"
            timestamp = msg.datetime.strftime("%H:%M")
            
            if msg.text_message:
                messages_text.append(f"[{timestamp}] {sender}: {msg.text_message}")
            elif msg.caption:
                messages_text.append(f"[{timestamp}] {sender}: (מדיה) {msg.caption}")
            else:
                messages_text.append(f"[{timestamp}] {sender}: (הודעת מדיה)")
        
        return {
            "chat_id": conversation.chat_id,
            "chat_name": conversation.chat_name or "לא ידוע",
            "last_message_time": conversation.last_message_time.strftime("%Y-%m-%d %H:%M"),
            "messages": messages_text,
            "message_count": len(conversation.messages),
            "is_unanswered": conversation.is_unanswered
        }
    
    def prioritize_conversations_by_time(self, conversations: List[ChatConversation]) -> List[ChatConversation]:
        """
        Prioritize conversations based on how long they've been unanswered
        
        Args:
            conversations: List of conversations to prioritize
        
        Returns:
            List of conversations sorted by priority
        """
        now = datetime.now()
        
        def get_priority_score(conv: ChatConversation) -> float:
            # Calculate hours since last message
            hours_since_last = (now - conv.last_message_time).total_seconds() / 3600
            
            # Higher score for older unanswered messages
            return hours_since_last
        
        # Sort by priority score (higher = more urgent)
        prioritized = sorted(conversations, key=get_priority_score, reverse=True)
        
        return prioritized
    
    def analyze_conversations(self, messages: List[GreenAPIMessage]) -> Tuple[List[ChatConversation], List[Dict]]:
        """
        Main analysis function - processes messages and returns prioritized conversations
        
        Args:
            messages: List of messages to analyze
        
        Returns:
            Tuple of (all conversations, open conversation summaries)
        """
        # Group messages by chat
        all_conversations = self.group_messages_by_chat(messages)
        
        # Identify open conversations
        open_conversations = self.identify_open_conversations(all_conversations)
        
        # Prioritize open conversations
        prioritized_open = self.prioritize_conversations_by_time(open_conversations)
        
        # Create summaries for AI analysis
        conversation_summaries = [
            self.get_conversation_summary(conv) for conv in prioritized_open
        ]
        
        return all_conversations, conversation_summaries
