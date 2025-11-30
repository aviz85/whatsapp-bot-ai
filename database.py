import sqlite3
import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
from models import GreenAPIMessage, PriorityReport, DashboardStats
from config import settings


class DatabaseManager:
    """SQLite database manager for storing message history and analytics"""
    
    def __init__(self):
        self.db_path = settings.database_url.replace("sqlite:///", "")
        self.logger = logging.getLogger(__name__)
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id TEXT UNIQUE NOT NULL,
                    type TEXT NOT NULL,
                    timestamp INTEGER NOT NULL,
                    type_message TEXT NOT NULL,
                    chat_id TEXT NOT NULL,
                    sender_id TEXT,
                    sender_name TEXT,
                    sender_contact_name TEXT,
                    text_message TEXT,
                    is_forwarded BOOLEAN DEFAULT FALSE,
                    forwarding_score INTEGER DEFAULT 0,
                    download_url TEXT,
                    caption TEXT,
                    file_name TEXT,
                    is_edited BOOLEAN DEFAULT FALSE,
                    is_deleted BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Conversations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id TEXT UNIQUE NOT NULL,
                    chat_name TEXT,
                    last_message_time TIMESTAMP NOT NULL,
                    message_count INTEGER DEFAULT 0,
                    is_unanswered BOOLEAN DEFAULT FALSE,
                    last_analyzed TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Analysis reports table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_date TIMESTAMP NOT NULL,
                    total_conversations INTEGER NOT NULL,
                    urgent_conversations INTEGER NOT NULL,
                    important_conversations INTEGER NOT NULL,
                    normal_conversations INTEGER NOT NULL,
                    summary TEXT NOT NULL,
                    report_data TEXT NOT NULL,  -- JSON data
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Statistics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE UNIQUE NOT NULL,
                    total_messages INTEGER DEFAULT 0,
                    unanswered_conversations INTEGER DEFAULT 0,
                    urgent_conversations INTEGER DEFAULT 0,
                    active_chats INTEGER DEFAULT 0,
                    analyses_run INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON messages(chat_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversations_chat_id ON conversations(chat_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_analysis_reports_date ON analysis_reports(report_date)')
            
            conn.commit()
            self.logger.info("Database initialized successfully")
    
    @contextmanager
    def get_connection(self):
        """Get database connection with proper error handling"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dictionary-like access
        try:
            yield conn
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def store_messages(self, messages: List[GreenAPIMessage]) -> int:
        """
        Store messages in database
        
        Args:
            messages: List of messages to store
        
        Returns:
            Number of new messages stored
        """
        if not messages:
            return 0
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            new_messages_count = 0
            
            for message in messages:
                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO messages (
                            message_id, type, timestamp, type_message, chat_id,
                            sender_id, sender_name, sender_contact_name, text_message,
                            is_forwarded, forwarding_score, download_url, caption,
                            file_name, is_edited, is_deleted
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        message.id_message, message.type, message.timestamp,
                        message.type_message, message.chat_id, message.sender_id,
                        message.sender_name, message.sender_contact_name,
                        message.text_message, message.is_forwarded,
                        message.forwarding_score, message.download_url,
                        message.caption, message.file_name, message.is_edited,
                        message.is_deleted
                    ))
                    
                    if cursor.rowcount > 0:
                        new_messages_count += 1
                
                except sqlite3.Error as e:
                    self.logger.error(f"Error storing message {message.id_message}: {e}")
                    continue
            
            conn.commit()
            self.logger.info(f"Stored {new_messages_count} new messages")
            return new_messages_count
    
    def update_conversation(self, chat_id: str, chat_name: Optional[str], 
                           last_message_time: datetime, message_count: int, 
                           is_unanswered: bool):
        """
        Update or insert conversation data
        
        Args:
            chat_id: Chat identifier
            chat_name: Chat display name
            last_message_time: Time of last message
            message_count: Number of messages in conversation
            is_unanswered: Whether conversation is unanswered
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO conversations (
                    chat_id, chat_name, last_message_time, message_count,
                    is_unanswered, last_analyzed, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                chat_id, chat_name, last_message_time, message_count,
                is_unanswered, datetime.now()
            ))
            
            conn.commit()
    
    def store_analysis_report(self, report: PriorityReport):
        """
        Store analysis report in database
        
        Args:
            report: PriorityReport to store
        """
        import json
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO analysis_reports (
                    report_date, total_conversations, urgent_conversations,
                    important_conversations, normal_conversations,
                    summary, report_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now(),
                report.total_conversations,
                len(report.urgent_conversations),
                len(report.important_conversations),
                len(report.normal_conversations),
                report.summary,
                json.dumps(report.dict(), ensure_ascii=False)
            ))
            
            conn.commit()
            self.logger.info("Analysis report stored successfully")
    
    def get_daily_stats(self, date: datetime = None) -> Dict[str, Any]:
        """
        Get daily statistics
        
        Args:
            date: Date to get stats for (default: today)
        
        Returns:
            Dictionary with daily statistics
        """
        if date is None:
            date = datetime.now().date()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM daily_stats WHERE date = ?
            ''', (date,))
            
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            else:
                # Return default stats if none exist
                return {
                    'date': date,
                    'total_messages': 0,
                    'unanswered_conversations': 0,
                    'urgent_conversations': 0,
                    'active_chats': 0,
                    'analyses_run': 0
                }
    
    def update_daily_stats(self, stats: Dict[str, Any]):
        """
        Update daily statistics
        
        Args:
            stats: Statistics to update
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO daily_stats (
                    date, total_messages, unanswered_conversations,
                    urgent_conversations, active_chats, analyses_run, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                stats.get('date', datetime.now().date()),
                stats.get('total_messages', 0),
                stats.get('unanswered_conversations', 0),
                stats.get('urgent_conversations', 0),
                stats.get('active_chats', 0),
                stats.get('analyses_run', 0)
            ))
            
            conn.commit()
    
    def get_recent_messages(self, limit: int = 100, chat_id: str = None) -> List[Dict[str, Any]]:
        """
        Get recent messages from database
        
        Args:
            limit: Maximum number of messages to return
            chat_id: Filter by specific chat ID (optional)
        
        Returns:
            List of message dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if chat_id:
                cursor.execute('''
                    SELECT * FROM messages 
                    WHERE chat_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (chat_id, limit))
            else:
                cursor.execute('''
                    SELECT * FROM messages 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_conversation_history(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get conversation history for the last N days
        
        Args:
            days: Number of days to look back
        
        Returns:
            List of conversation statistics
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            since_date = datetime.now() - timedelta(days=days)
            
            cursor.execute('''
                SELECT 
                    DATE(last_message_time) as date,
                    COUNT(*) as conversations,
                    SUM(CASE WHEN is_unanswered = 1 THEN 1 ELSE 0 END) as unanswered,
                    AVG(message_count) as avg_messages_per_chat
                FROM conversations 
                WHERE last_message_time >= ?
                GROUP BY DATE(last_message_time)
                ORDER BY date DESC
            ''', (since_date,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_analysis_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent analysis reports
        
        Args:
            limit: Maximum number of reports to return
        
        Returns:
            List of analysis report summaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    id, report_date, total_conversations, 
                    urgent_conversations, important_conversations,
                    normal_conversations, summary
                FROM analysis_reports 
                ORDER BY report_date DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """
        Clean up old data to prevent database bloat
        
        Args:
            days_to_keep: Number of days to keep data
        """
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Clean up old messages
            cursor.execute('DELETE FROM messages WHERE timestamp < ?', (cutoff_date.timestamp(),))
            messages_deleted = cursor.rowcount
            
            # Clean up old analysis reports
            cursor.execute('DELETE FROM analysis_reports WHERE report_date < ?', (cutoff_date,))
            reports_deleted = cursor.rowcount
            
            conn.commit()
            
            self.logger.info(f"Cleaned up {messages_deleted} old messages and {reports_deleted} old reports")
    
    def get_latest_analysis_report(self) -> Optional[Dict[str, Any]]:
        """
        Get the latest analysis report from database
        
        Returns:
            Dictionary with report data or None if no reports exist
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT report_data FROM analysis_reports
                ORDER BY report_date DESC
                LIMIT 1
            ''')
            
            row = cursor.fetchone()
            
            if row:
                return json.loads(row['report_data'])
            return None
    
    def get_messages_by_chat(self, chat_id: str, limit: int = 4) -> List[Dict[str, Any]]:
        """
        Get last N messages for a specific chat
        
        Args:
            chat_id: Chat ID to get messages for
            limit: Number of messages to retrieve (default: 4)
        
        Returns:
            List of message dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM messages
                WHERE chat_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (chat_id, limit))
            
            rows = cursor.fetchall()
            
            # Convert to list of dicts and reverse to get chronological order
            messages = [dict(row) for row in rows]
            messages.reverse()
            
            return messages


# Global database instance
db = DatabaseManager()
