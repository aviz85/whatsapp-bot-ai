"""
Cron scheduler for automated WhatsApp bot analysis
"""
import logging
import asyncio
from datetime import datetime
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from config import settings

logger = logging.getLogger(__name__)


class CronScheduler:
    """Manages scheduled analysis jobs"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.job = None
        self.is_running = False
        
    async def run_scheduled_analysis(self):
        """Run the analysis job"""
        try:
            logger.info("Running scheduled analysis...")
            from whatsapp_bot import bot
            
            result = await bot.analyze_and_report(
                target_chat_id=None,
                minutes=settings.message_analysis_minutes
            )
            
            logger.info(f"Scheduled analysis completed: {result}")
            
        except Exception as e:
            logger.error(f"Scheduled analysis failed: {e}")
    
    def start(self, cron_expression: str = None):
        """
        Start the cron scheduler
        
        Args:
            cron_expression: Cron expression (e.g., "0 9 * * *" for 9 AM daily)
        """
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        cron_expr = cron_expression or settings.cron_schedule
        
        # Re-initialize scheduler to ensure clean state after shutdown
        self.scheduler = AsyncIOScheduler()
        
        try:
            # Parse cron expression
            parts = cron_expr.split()
            if len(parts) != 5:
                raise ValueError("Invalid cron expression. Expected format: 'minute hour day month day_of_week'")
            
            minute, hour, day, month, day_of_week = parts
            
            # Create cron trigger
            trigger = CronTrigger(
                minute=minute,
                hour=hour,
                day=day,
                month=month,
                day_of_week=day_of_week
            )
            
            # Add job
            self.job = self.scheduler.add_job(
                self.run_scheduled_analysis,
                trigger=trigger,
                id='whatsapp_analysis',
                name='WhatsApp Message Analysis',
                replace_existing=True
            )
            
            # Start scheduler
            self.scheduler.start()
            self.is_running = True
            
            logger.info(f"Cron scheduler started with expression: {cron_expr}")
            logger.info(f"Next run time: {self.job.next_run_time}")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise
    
    def stop(self):
        """Stop the cron scheduler"""
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return
        
        try:
            self.scheduler.shutdown(wait=False)
            self.is_running = False
            logger.info("Cron scheduler stopped")
        except Exception as e:
            logger.error(f"Failed to stop scheduler: {e}")
    
    def get_status(self) -> dict:
        """Get scheduler status"""
        if not self.is_running:
            return {
                "enabled": False,
                "schedule": settings.cron_schedule,
                "next_run": None
            }
        
        return {
            "enabled": True,
            "schedule": settings.cron_schedule,
            "next_run": self.job.next_run_time.isoformat() if self.job and self.job.next_run_time else None
        }
    
    def update_schedule(self, cron_expression: str):
        """
        Update the cron schedule
        
        Args:
            cron_expression: New cron expression
        """
        was_running = self.is_running
        
        if was_running:
            self.stop()
        
        # Update settings
        settings.cron_schedule = cron_expression
        
        if was_running:
            self.start(cron_expression)


# Global scheduler instance
scheduler = CronScheduler()
