import logging
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any
from green_api_client import GreenAPIClient
from message_analyzer import MessageAnalyzer
from openrouter_client import OpenRouterClient
from models import GreenAPIMessage, PriorityReport, DashboardStats
from config import settings
from database import db


class WhatsAppBot:
    """Main WhatsApp bot service that coordinates all components"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.green_client = GreenAPIClient()
        self.message_analyzer = MessageAnalyzer()
        self.openrouter_client = OpenRouterClient()
        
        # Statistics tracking
        self.stats = DashboardStats(
            total_messages=0,
            unanswered_conversations=0,
            urgent_conversations=0,
            last_analysis_time=datetime.now(),
            active_chats=0
        )
    
    async def analyze_and_report(self, target_chat_id: Optional[str] = None, minutes: int = None) -> Dict[str, Any]:
        """
        Main method to analyze messages and generate report
        
        Args:
            target_chat_id: Chat ID to send the report to (if None, sends to self)
            minutes: Time period in minutes to analyze (default from settings)
        
        Returns:
            Dictionary with analysis results
        """
        try:
            if minutes is None:
                minutes = settings.message_analysis_minutes
            
            self.logger.info(f"Starting message analysis for the last {minutes} minutes")
            
            # Step 1: Fetch messages from Green API
            messages = self.green_client.get_last_incoming_messages(minutes=minutes)
            
            if not messages:
                self.logger.info("No messages found for analysis")
                return {
                    "success": True,
                    "message": "No messages found for analysis",
                    "report": None
                }
            
            # Store messages in database
            new_messages_count = db.store_messages(messages)
            self.logger.info(f"Stored {new_messages_count} new messages in database")
            
            # Update statistics
            self.stats.total_messages = len(messages)
            self.stats.last_analysis_time = datetime.now()
            
            # Step 2: Analyze messages and identify open conversations
            all_conversations, conversation_summaries = self.message_analyzer.analyze_conversations(messages)
            
            # Update conversations in database
            for conv in all_conversations:
                db.update_conversation(
                    conv.chat_id, conv.chat_name, conv.last_message_time,
                    len(conv.messages), conv.is_unanswered
                )
            
            # Update statistics
            self.stats.active_chats = len(all_conversations)
            self.stats.unanswered_conversations = len(conversation_summaries)
            
            if not conversation_summaries:
                self.logger.info("No open conversations found")
                empty_report = PriorityReport(
                    urgent_conversations=[],
                    important_conversations=[],
                    normal_conversations=[],
                    summary="לא נמצאו שיחות פתוחות. כל ההודעות נענו!",
                    total_conversations=0
                )
                
                # Send empty report
                await self._send_report(empty_report, target_chat_id)
                
                return {
                    "success": True,
                    "message": "No open conversations found",
                    "report": empty_report.dict(),
                    "stats": self.stats.dict()
                }
            
            # Step 3: Send to OpenRouter for prioritization
            self.logger.info("Sending conversations to AI for prioritization")
            priority_report = self.openrouter_client.analyze_conversations(conversation_summaries)
            
            # Update statistics
            self.stats.urgent_conversations = len(priority_report.urgent_conversations)
            
            # Store analysis report in database
            db.store_analysis_report(priority_report)
            
            # Update daily statistics
            daily_stats = {
                'date': datetime.now().date(),
                'total_messages': self.stats.total_messages,
                'unanswered_conversations': self.stats.unanswered_conversations,
                'urgent_conversations': self.stats.urgent_conversations,
                'active_chats': self.stats.active_chats,
                'analyses_run': 1  # This will be incremented in DB
            }
            db.update_daily_stats(daily_stats)
            
            # Step 4: Generate and send report
            await self._send_report(priority_report, target_chat_id)
            
            self.logger.info("Analysis and reporting completed successfully")
            
            return {
                "success": True,
                "message": f"Analysis completed. Found {priority_report.total_conversations} open conversations.",
                "report": priority_report.dict(),
                "stats": self.stats.dict()
            }
        
        except Exception as e:
            self.logger.error(f"Error during analysis and reporting: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "report": None,
                "stats": self.stats.dict()
            }
    
    async def analyze_and_report_with_progress(self, target_chat_id: Optional[str] = None, 
                                          minutes: int = 1440, progress_callback=None) -> Dict[str, Any]:
        """
        Analyze messages and generate report with progress tracking
        
        Args:
            target_chat_id: Chat ID to send report to (if None, sends to configured user)
            minutes: Time period in minutes to analyze
            progress_callback: Function to call with progress updates
        
        Returns:
            Analysis results
        """
        try:
            # Step 1: Fetch messages from Green API
            if progress_callback:
                progress_callback(10, "מושך הודעות מה-API...", "מתחבר ל-Green API")
            
            messages = self.green_client.get_last_incoming_messages(minutes=minutes)
            
            if not messages:
                if progress_callback:
                    progress_callback(100, "✅ ניתוח הסתיים", "לא נמצאו הודעות לניתוח")
                
                return {
                    "success": True,
                    "message": "No messages found for analysis",
                    "report": None
                }
            
            # Store messages in database
            new_messages_count = db.store_messages(messages)
            self.logger.info(f"Stored {new_messages_count} new messages in database")
            
            if progress_callback:
                progress_callback(30, "מאתר שיחות פתוחות...", f"נמצאו {len(messages)} הודעות")
            
            # Update statistics
            self.stats.total_messages = len(messages)
            self.stats.last_analysis_time = datetime.now()
            
            # Step 2: Analyze messages and identify open conversations
            if progress_callback:
                progress_callback(50, "מקבץ הודעות לפי צ'אטים...", "מזהה שיחות שלא נענו")
            
            all_conversations, conversation_summaries = self.message_analyzer.analyze_conversations(messages)
            
            # Update conversations in database
            for conv in all_conversations:
                db.update_conversation(
                    conv.chat_id, conv.chat_name, conv.last_message_time,
                    len(conv.messages), conv.is_unanswered
                )
            
            # Update statistics
            self.stats.active_chats = len(all_conversations)
            self.stats.unanswered_conversations = len(conversation_summaries)
            
            if not conversation_summaries:
                if progress_callback:
                    progress_callback(100, "✅ ניתוח הסתיים", "לא נמצאו שיחות פתוחות")
                
                empty_report = PriorityReport(
                    urgent_conversations=[],
                    important_conversations=[],
                    normal_conversations=[],
                    summary="לא נמצאו שיחות פתוחות הדורשות תגובה."
                )
                
                return {
                    "success": True,
                    "message": "No open conversations found",
                    "report": empty_report.dict(),
                    "stats": self.stats.dict()
                }
            
            # Step 3: Send to OpenRouter for prioritization
            if progress_callback:
                progress_callback(70, "שולח ל-AI לניתוח...", f"מנתח {len(conversation_summaries)} שיחות פתוחות")
            
            priority_report = self.openrouter_client.analyze_conversations(conversation_summaries)
            
            # Update statistics
            self.stats.urgent_conversations = len(priority_report.urgent_conversations)
            
            # Store analysis report in database
            db.store_analysis_report(priority_report)
            
            # Update daily statistics
            daily_stats = {
                'date': datetime.now().date(),
                'total_messages': self.stats.total_messages,
                'unanswered_conversations': self.stats.unanswered_conversations,
                'urgent_conversations': self.stats.urgent_conversations,
                'active_chats': self.stats.active_chats,
                'analyses_run': 1
            }
            db.update_daily_stats(daily_stats)
            
            # Step 4: Generate and send report
            if progress_callback:
                progress_callback(90, "מכין דוח...", "מסדר תוצאות לפי דחיפות")
            
            await self._send_report(priority_report, target_chat_id)
            
            if progress_callback:
                progress_callback(100, "✅ ניתוח הסתיים בהצלחה!", f"נמצאו {priority_report.total_conversations} שיחות פתוחות")
            
            self.logger.info("Analysis and reporting completed successfully")
            
            return {
                "success": True,
                "message": f"Analysis completed. Found {priority_report.total_conversations} open conversations.",
                "report": priority_report.dict(),
                "stats": self.stats.dict()
            }
        
        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            if progress_callback:
                progress_callback(100, "❌ שגיאה בניתוח", str(e))
            raise
    
    async def _send_report(self, report: PriorityReport, target_chat_id: Optional[str] = None):
        """
        Send the priority report via WhatsApp
        
        Args:
            report: PriorityReport to send
            target_chat_id: Chat ID to send to (if None, sends to user's configured number)
        """
        try:
            self.logger.info("=== Starting _send_report ===")
            self.logger.info(f"Report type: {type(report)}")
            self.logger.info(f"Target chat ID: {target_chat_id}")
            
            # Generate formatted report
            self.logger.info("Generating formatted report...")
            formatted_report = self.openrouter_client.generate_summary_report(report)
            self.logger.info(f"Formatted report length: {len(formatted_report)} characters")
            
            # If no target chat specified, send to user's configured phone number
            if target_chat_id is None:
                self.logger.info("No target chat specified, determining recipient...")
                self.logger.info(f"User phone number from settings: {settings.user_phone_number}")
                
                if settings.user_phone_number:
                    target_chat_id = f"{settings.user_phone_number}@c.us"
                    self.logger.info(f"Using user phone number: {target_chat_id}")
                else:
                    # Fallback to instance ID if no user phone configured
                    target_chat_id = f"{settings.green_api_id_instance}@c.us"
                    self.logger.info(f"Using instance ID as fallback: {target_chat_id}")
            
            # Send the report
            self.logger.info(f"Sending message to {target_chat_id}...")
            result = self.green_client.send_message(target_chat_id, formatted_report)
            
            self.logger.info(f"Report sent successfully to {target_chat_id}")
            self.logger.info(f"Send result: {result}")
            
            return result
        
        except Exception as e:
            self.logger.error(f"Failed to send report: {e}")
            self.logger.error(f"Exception type: {type(e)}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    async def send_custom_message(self, chat_id: str, message: str) -> Dict[str, Any]:
        """
        Send a custom message to a specific chat
        
        Args:
            chat_id: Target chat ID
            message: Message to send
        
        Returns:
            Result from Green API
        """
        try:
            result = self.green_client.send_message(chat_id, message)
            self.logger.info(f"Custom message sent to {chat_id}")
            return result
        
        except Exception as e:
            self.logger.error(f"Failed to send custom message: {e}")
            raise
    
    def get_account_status(self) -> Dict[str, Any]:
        """
        Get the current account status and settings
        
        Returns:
            Account information from Green API
        """
        try:
            account_info = self.green_client.get_account_info()
            return {
                "success": True,
                "account_info": account_info,
                "bot_stats": self.stats.dict()
            }
        
        except Exception as e:
            self.logger.error(f"Failed to get account status: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "account_info": None,
                "bot_stats": self.stats.dict()
            }
    
    def get_recent_messages(self, minutes: int = 60, use_database: bool = True) -> List[Dict[str, Any]]:
        """
        Get recent messages for debugging/monitoring
        
        Args:
            minutes: Time period in minutes
            use_database: Whether to fetch from database (default) or API
        
        Returns:
            List of recent messages
        """
        try:
            if use_database:
                # Get from database for better performance
                return db.get_recent_messages(limit=100)
            else:
                # Get from API
                messages = self.green_client.get_last_incoming_messages(minutes=minutes)
                return [msg.dict() for msg in messages]
        
        except Exception as e:
            self.logger.error(f"Failed to get recent messages: {e}")
            return []
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get statistics from database
        
        Returns:
            Database statistics
        """
        try:
            daily_stats = db.get_daily_stats()
            conversation_history = db.get_conversation_history(days=7)
            analysis_history = db.get_analysis_history(limit=5)
            
            return {
                "daily_stats": daily_stats,
                "conversation_history": conversation_history,
                "analysis_history": analysis_history
            }
        
        except Exception as e:
            self.logger.error(f"Failed to get database stats: {e}")
            return {}
    
    async def run_scheduled_analysis(self, interval_minutes: int = 30):
        """
        Run analysis on a schedule (for background processing)
        
        Args:
            interval_minutes: Interval between analyses in minutes
        """
        self.logger.info(f"Starting scheduled analysis every {interval_minutes} minutes")
        
        while True:
            try:
                await self.analyze_and_report()
                await asyncio.sleep(interval_minutes * 60)
            
            except Exception as e:
                self.logger.error(f"Error in scheduled analysis: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying


# Global bot instance
bot = WhatsAppBot()
