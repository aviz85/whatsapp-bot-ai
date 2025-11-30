import logging
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn
from datetime import datetime
import asyncio

from config import settings
from whatsapp_bot import bot
from database import db
from ai_models import AVAILABLE_MODELS, get_models_by_provider, get_providers
from cron_scheduler import scheduler


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Progress tracking
analysis_progress = {
    "status": "idle",
    "progress": 0,
    "message": "",
    "details": "",
    "start_time": None
}

# Create FastAPI app
app = FastAPI(
    title="WhatsApp Bot Dashboard",
    description="Dashboard for managing WhatsApp bot with Green API and OpenRouter integration",
    version="1.0.0"
)

# Setup templates with custom filters
def timestamp_to_datetime(timestamp):
    """Convert timestamp to readable datetime"""
    try:
        dt = datetime.fromtimestamp(int(timestamp))
        return dt.strftime('%H:%M %d/%m/%Y')
    except:
        return timestamp

templates = Jinja2Templates(directory="templates")
templates.env.filters['timestamp_to_datetime'] = timestamp_to_datetime

# Pydantic models for API requests
class AnalysisRequest(BaseModel):
    minutes: Optional[int] = 1440
    target_chat_id: Optional[str] = None
    config: Optional[Dict[str, Any]] = None  # Config from localStorage

class MessageRequest(BaseModel):
    chat_id: str
    message: str

class ConfigUpdate(BaseModel):
    green_api_url: Optional[str] = None
    green_api_id_instance: Optional[str] = None
    green_api_token_instance: Optional[str] = None
    user_phone_number: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    openrouter_model: Optional[str] = None
    analysis_interval: Optional[int] = None

class CronScheduleUpdate(BaseModel):
    enabled: bool
    schedule: Optional[str] = None  # Cron expression: "minute hour day month day_of_week"



@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page - NO Green API calls, only database"""
    try:
        # Get stats from bot (in-memory, no API calls)
        bot_stats = bot.stats.dict() if hasattr(bot, 'stats') else {
            "total_messages": 0,
            "unanswered_conversations": 0,
            "urgent_conversations": 0,
            "active_chats": 0
        }
        
        # Get recent messages from database ONLY
        recent_messages = bot.get_recent_messages(minutes=60, use_database=True)
        
        # Get latest report stats from database
        latest_report = db.get_latest_analysis_report()
        if latest_report:
            bot_stats["unanswered_conversations"] = latest_report.get("total_conversations", 0)
            bot_stats["urgent_conversations"] = len(latest_report.get("urgent_conversations", []))
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "status": {
                "account_status": "cached",
                "bot_stats": bot_stats
            },
            "recent_messages": recent_messages[:10],  # Show last 10 messages
            "stats": bot_stats,
            "settings": {
                "green_api_url": settings.green_api_url,
                "green_api_id_instance": settings.green_api_id_instance,
                "green_api_token_instance": settings.green_api_token_instance,
                "user_phone_number": settings.user_phone_number,
                "openrouter_api_key": settings.openrouter_api_key
            }
        })
    except Exception as e:
        logging.error(f"Error loading dashboard: {e}")
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": str(e)
        })


@app.post("/api/analyze")
async def analyze_messages(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Trigger message analysis with progress tracking"""
    global analysis_progress
    
    # Apply config from localStorage if provided
    if request.config:
        from config_injector import config_injector
        is_valid, error_msg = config_injector.validate_config(request.config)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        config_injector.apply_config(request.config)
    
    # Reset progress
    analysis_progress = {
        "status": "starting",
        "progress": 0,
        "message": "מתחיל ניתוח...",
        "details": "מתחבר ל-Green API",
        "start_time": datetime.now()
    }
    
    try:
        # Run analysis in background with progress updates
        result = await bot.analyze_and_report_with_progress(
            target_chat_id=request.target_chat_id,
            minutes=request.minutes,
            progress_callback=update_progress
        )
        
        # Final progress update
        analysis_progress.update({
            "status": "completed",
            "progress": 100,
            "message": "✅ ניתוח הסתיים בהצלחה!",
            "details": f"נמצאו {result.get('report', {}).get('total_conversations', 0)} שיחות פתוחות"
        })
        
        return result
    except Exception as e:
        logging.error(f"Error in analysis: {e}")
        analysis_progress.update({
            "status": "error",
            "progress": 100,
            "message": "❌ שגיאה בניתוח",
            "details": str(e)
        })
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/progress")
async def get_analysis_progress():
    """Get current analysis progress"""
    return analysis_progress

def update_progress(progress: int, message: str, details: str = ""):
    """Update analysis progress"""
    global analysis_progress
    analysis_progress.update({
        "progress": progress,
        "message": message,
        "details": details
    })
    logging.info(f"Progress: {progress}% - {message} - {details}")


@app.post("/api/send-message")
async def send_message(request: MessageRequest):
    """Send a custom message"""
    try:
        result = await bot.send_custom_message(
            chat_id=request.chat_id,
            message=request.message
        )
        return {"success": True, "result": result}
    except Exception as e:
        logging.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/status")
async def get_status():
    """Get current bot status - NO Green API calls, only cached data"""
    try:
        # Get stats from memory and database - NO API CALLS
        bot_stats = bot.stats.dict() if hasattr(bot, 'stats') else {
            "total_messages": 0,
            "unanswered_conversations": 0,
            "urgent_conversations": 0,
            "active_chats": 0
        }
        
        # Update from latest report in database
        latest_report = db.get_latest_analysis_report()
        if latest_report:
            bot_stats["unanswered_conversations"] = latest_report.get("total_conversations", 0)
            bot_stats["urgent_conversations"] = len(latest_report.get("urgent_conversations", []))
        
        return {
            "account_status": "cached",
            "bot_stats": bot_stats,
            "message": "Data from cache and database"
        }
    except Exception as e:
        logging.error(f"Error getting status: {e}")
        return {
            "account_status": "error",
            "bot_stats": {},
            "message": str(e)
        }


@app.get("/api/messages")
async def get_messages(minutes: int = 60, use_database: bool = True, exclude_groups: bool = False):
    """Get recent messages - ALWAYS from database by default"""
    try:
        # Force database usage to avoid API calls
        messages = bot.get_recent_messages(minutes=minutes, use_database=True)
        
        # Filter out group messages if requested
        if exclude_groups:
            messages = [msg for msg in messages if not (msg.get('chat_id', '').endswith('@g.us'))]
        
        return {"success": True, "messages": messages}
    except Exception as e:
        logging.error(f"Error getting messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/refresh-from-green")
async def refresh_from_green(minutes: int = 60):
    """
    Manually refresh data from Green API - USE SPARINGLY!
    This is the ONLY endpoint that calls Green API for messages.
    """
    try:
        logging.info(f"Manual refresh from Green API requested for last {minutes} minutes")
        
        # Fetch from Green API and store in database
        messages = bot.get_recent_messages(minutes=minutes, use_database=False)
        
        return {
            "success": True,
            "message": f"Fetched {len(messages)} messages from Green API",
            "messages_count": len(messages)
        }
    except Exception as e:
        logging.error(f"Error refreshing from Green API: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/database-stats")
async def get_database_stats():
    """Get database statistics"""
    try:
        stats = bot.get_database_stats()
        return {"success": True, "stats": stats}
    except Exception as e:
        logging.error(f"Error getting database stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/urgent-conversations")
async def get_urgent_conversations():
    """Get urgent conversations with their last 4 messages"""
    try:
        # Get the latest analysis report from database
        latest_report = db.get_latest_analysis_report()
        
        if not latest_report:
            return {"success": True, "conversations": []}
        
        urgent_convs = []
        
        # Get urgent conversations from the report
        for conv_data in latest_report.get('urgent_conversations', []):
            chat_id = conv_data.get('chat_id')
            
            # Get last 4 messages for this chat from database
            messages = db.get_messages_by_chat(chat_id, limit=4)
            
            urgent_convs.append({
                'chat_id': chat_id,
                'chat_name': conv_data.get('chat_name'),
                'reason': conv_data.get('reason'),
                'messages': messages
            })
        
        return {"success": True, "conversations": urgent_convs}
    except Exception as e:
        logging.error(f"Error getting urgent conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/config")
async def update_config(request: ConfigUpdate):
    """Update configuration (in-memory only for demo)"""
    try:
        updates = {}
        
        if request.green_api_url:
            settings.green_api_url = request.green_api_url
            updates["green_api_url"] = "Updated"
        
        if request.green_api_id_instance:
            settings.green_api_id_instance = request.green_api_id_instance
            updates["green_api_id_instance"] = "Updated"
        
        if request.green_api_token_instance:
            settings.green_api_token_instance = request.green_api_token_instance
            updates["green_api_token_instance"] = "Updated"
        
        if request.user_phone_number:
            settings.user_phone_number = request.user_phone_number
            updates["user_phone_number"] = "Updated"
        
        if request.openrouter_api_key:
            settings.openrouter_api_key = request.openrouter_api_key
            updates["openrouter_api_key"] = "Updated"
        
        if request.openrouter_model:
            settings.openrouter_model = request.openrouter_model
            updates["openrouter_model"] = request.openrouter_model
        
        if request.analysis_interval:
            settings.message_analysis_minutes = request.analysis_interval
            updates["analysis_interval"] = request.analysis_interval
        
        return {
            "success": True,
            "message": "Configuration updated",
            "updates": updates
        }
    except Exception as e:
        logging.error(f"Error updating config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/models")
async def get_available_models():
    """Get list of available AI models"""
    try:
        return {
            "success": True,
            "models": AVAILABLE_MODELS,
            "providers": get_providers()
        }
    except Exception as e:
        logging.error(f"Error getting models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/cron/status")
async def get_cron_status():
    """Get cron scheduler status"""
    try:
        status = scheduler.get_status()
        return {
            "success": True,
            **status
        }
    except Exception as e:
        logging.error(f"Error getting cron status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/cron/update")
async def update_cron_schedule(request: CronScheduleUpdate):
    """Update cron schedule"""
    try:
        if request.enabled:
            # Start or update scheduler
            schedule = request.schedule or settings.cron_schedule
            scheduler.start(schedule)
            message = f"Cron scheduler enabled with schedule: {schedule}"
        else:
            # Stop scheduler
            scheduler.stop()
            message = "Cron scheduler disabled"
        
        return {
            "success": True,
            "message": message,
            "status": scheduler.get_status()
        }
    except Exception as e:
        logging.error(f"Error updating cron schedule: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug
    )
