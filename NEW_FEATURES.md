# WhatsApp Bot - New Features Guide

## 🎉 What's New

### 1. **localStorage-Based Configuration** 🔐
API keys are now stored **only in your browser** (localStorage), not on the server!

#### Benefits:
- ✅ **More secure** - credentials never stored on server
- ✅ **Privacy** - each user has their own config
- ✅ **Portable** - use different configs in different browsers
- ✅ **No .env needed** - configure everything via dashboard

#### How it works:
1. Open dashboard → Click "⚙️ הגדרות"
2. Go to "🔑 API Keys" tab
3. Enter your credentials:
   - Green API URL
   - ID Instance
   - API Token
   - Phone Number
   - OpenRouter API Key
4. Click "💾 שמור הגדרות"
5. Credentials are saved in browser localStorage
6. Every API call automatically includes your config

#### Important Notes:
⚠️ **Config is browser-specific**
- If you clear browser cache, you'll need to re-enter
- Different browsers = different configs
- Incognito mode won't save config

⚠️ **Security**
- localStorage is accessible to JavaScript
- Don't use on shared/public computers
- For production, consider additional encryption

---

### 2. **AI Model Selection** 🤖
Choose from multiple AI models for message analysis!

#### Available Models:

**Claude (Anthropic)**
- `anthropic/claude-opus-4.5` - Most capable, best for complex reasoning
- `anthropic/claude-3.7-sonnet` - Balanced performance
- `anthropic/claude-3.5-sonnet` - Fast and efficient

**Gemini (Google)**
- `google/gemini-3-pro` - Flagship model, 1M tokens
- `google/gemini-2.5-pro` - Advanced reasoning
- `google/gemini-2.5-flash` - Fast and efficient
- `google/gemini-flash-1.5` - Lightweight

**GPT (OpenAI)**
- `openai/gpt-5.1` - Latest frontier model
- `openai/gpt-5.1-chat` - Fast, low-latency
- `openai/gpt-5` - Advanced reasoning
- `openai/gpt-4o` - Optimized GPT-4 (default)
- `openai/gpt-4-turbo` - Faster variant

**Grok (xAI)**
- `x-ai/grok-4.1-fast` - Best for agentic tasks
- `x-ai/grok-4` - Latest with vision
- `x-ai/grok-3` - Enterprise flagship
- `x-ai/grok-3-mini` - Lightweight

#### How to Select:
1. Settings → "🤖 AI Model" tab
2. Filter by provider (optional)
3. Choose model from dropdown
4. See model info (description, context length)
5. Save settings

#### Model Comparison:

| Model | Speed | Cost | Quality | Context |
|-------|-------|------|---------|---------|
| GPT-4o | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | 128K |
| Claude Opus 4.5 | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | 200K |
| Gemini 3 Pro | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 1M |
| Grok 4.1 Fast | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | 2M |

---

### 3. **Cron Job Scheduler** ⏰
Automate analysis to run at specific times!

#### Features:
- ✅ Schedule daily/weekly/hourly analysis
- ✅ Predefined templates (9 AM daily, every 6 hours, etc.)
- ✅ Custom cron expressions
- ✅ View next run time
- ✅ Enable/disable easily

#### How to Setup:

**Method 1: Use Presets**
1. Settings → "⏰ Cron Schedule" tab
2. Check "אפשר תזמון אוטומטי"
3. Select from presets:
   - Every day at 9:00 AM
   - Every day at 12:00 PM
   - Every day at 6:00 PM
   - Every Monday at 9:00 AM
   - Every weekday at 9:00 AM
   - Every 6 hours
4. Save settings

**Method 2: Custom Cron**
1. Select "מותאם אישית..." from presets
2. Enter cron expression
3. Save settings

#### Cron Expression Format:
```
minute hour day month day_of_week
```

**Examples:**
```bash
0 9 * * *       # Every day at 9:00 AM
0 */6 * * *     # Every 6 hours
30 8 * * 1-5    # Weekdays at 8:30 AM
0 12,18 * * *   # Daily at 12:00 PM and 6:00 PM
*/30 * * * *    # Every 30 minutes
0 0 1 * *       # First day of month at midnight
```

#### Cron Status:
- View current status (active/inactive)
- See next scheduled run time
- Enable/disable without losing schedule

---

## 🚀 Quick Start Guide

### First Time Setup:

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Start Server**
```bash
python main.py
```

3. **Open Dashboard**
```
http://localhost:8000
```

4. **Configure API Keys**
- Click "⚙️ הגדרות"
- Enter Green API credentials
- Enter OpenRouter API key
- Choose AI model
- Save

5. **Setup Cron (Optional)**
- Go to Cron Schedule tab
- Enable and select schedule
- Save

6. **Run Analysis**
- Click "🔍 נתח הודעות"
- Wait for completion
- View results

---

## 📊 API Endpoints

### New Endpoints:

#### Get Available Models
```bash
GET /api/models
```

**Response:**
```json
{
  "success": true,
  "models": [
    {
      "id": "openai/gpt-4o",
      "name": "GPT-4o",
      "provider": "OpenAI",
      "description": "Optimized GPT-4 model",
      "context": "128K tokens"
    },
    ...
  ],
  "providers": ["OpenAI", "Anthropic", "Google", "xAI"]
}
```

#### Get Cron Status
```bash
GET /api/cron/status
```

**Response:**
```json
{
  "success": true,
  "enabled": true,
  "schedule": "0 9 * * *",
  "next_run": "2025-12-01T09:00:00"
}
```

#### Update Cron Schedule
```bash
POST /api/cron/update
Content-Type: application/json

{
  "enabled": true,
  "schedule": "0 9 * * *"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Cron scheduler enabled with schedule: 0 9 * * *",
  "status": {
    "enabled": true,
    "schedule": "0 9 * * *",
    "next_run": "2025-12-01T09:00:00"
  }
}
```

---

## 🔧 Configuration Files

### New Files:

1. **`ai_models.py`** - AI model definitions
2. **`cron_scheduler.py`** - Cron job manager
3. **`config_injector.py`** - localStorage config handler
4. **`templates/dashboard_new.html`** - Enhanced dashboard

### Updated Files:

1. **`config.py`** - Made API keys optional
2. **`main.py`** - Added new endpoints
3. **`requirements.txt`** - Added APScheduler

---

## 💡 Usage Examples

### Example 1: Daily Morning Report
```
Schedule: 0 9 * * *
Result: Bot analyzes messages every day at 9 AM
        Sends report to your WhatsApp
```

### Example 2: Hourly Monitoring
```
Schedule: 0 * * * *
Result: Bot checks every hour
        Alerts on urgent conversations
```

### Example 3: Weekday Business Hours
```
Schedule: 0 9-17 * * 1-5
Result: Every hour from 9 AM to 5 PM
        Monday to Friday only
```

---

## 🔐 Security Best Practices

### localStorage Security:

1. **Don't use on public computers**
   - Config is stored in browser
   - Anyone with access can see it

2. **Use HTTPS in production**
   - Encrypt data in transit
   - Prevent man-in-the-middle attacks

3. **Regular key rotation**
   - Change API keys periodically
   - Update in dashboard settings

4. **Browser security**
   - Keep browser updated
   - Use trusted extensions only
   - Clear cache when needed

---

## 🐛 Troubleshooting

### Config Not Saving?
- Check browser console for errors
- Ensure localStorage is enabled
- Try different browser

### Cron Not Running?
- Check cron status in settings
- Verify cron expression is valid
- Check server logs for errors

### API Calls Failing?
- Verify API keys in settings
- Check config status on dashboard
- Test with "🔍 נתח הודעות" button

### Model Not Available?
- Check OpenRouter account
- Verify API key has access
- Try different model

---

## 📝 Migration Guide

### From Old Version:

1. **Backup .env file**
```bash
cp .env .env.backup
```

2. **Update code**
```bash
git pull
pip install -r requirements.txt
```

3. **Transfer config to dashboard**
- Open dashboard
- Go to settings
- Enter API keys from .env
- Save

4. **Optional: Remove .env**
```bash
# Keep as backup or remove
rm .env
```

---

## 🎯 Tips & Tricks

### Tip 1: Multiple Configs
Use different browsers for different accounts:
- Chrome: Personal account
- Firefox: Business account
- Safari: Testing account

### Tip 2: Model Selection
- **Fast analysis**: Use Gemini Flash or GPT-4 Turbo
- **Best quality**: Use Claude Opus or GPT-5.1
- **Cost-effective**: Use Grok Mini or Gemini Flash

### Tip 3: Cron Schedules
- **High volume**: Every 30 minutes
- **Medium volume**: Every 2-3 hours
- **Low volume**: Once or twice daily

### Tip 4: Testing
Test cron schedule before enabling:
1. Set to run in 5 minutes
2. Verify it works
3. Update to desired schedule

---

## 🆘 Support

### Common Issues:

**Issue**: "Missing required fields" error
**Solution**: Ensure all API keys are entered in settings

**Issue**: Cron not triggering
**Solution**: Check server is running continuously

**Issue**: Wrong model used
**Solution**: Verify model selection in settings, save again

**Issue**: Config lost after restart
**Solution**: This is normal - config is in browser, not server

---

## 🔄 Changelog

### Version 2.0 (Current)

**Added:**
- ✅ localStorage-based configuration
- ✅ Multiple AI model support (16 models)
- ✅ Cron job scheduler
- ✅ Enhanced settings UI with tabs
- ✅ Model info display
- ✅ Cron status monitoring

**Changed:**
- ⚙️ API keys now optional in .env
- ⚙️ Config injected from request body
- ⚙️ Dashboard redesigned with tabs

**Fixed:**
- 🐛 Config persistence issues
- 🐛 Model selection bugs

---

## 📚 Additional Resources

- [OpenRouter Models](https://openrouter.ai/models)
- [Cron Expression Generator](https://crontab.guru/)
- [Green API Documentation](https://green-api.com/docs/)
- [APScheduler Documentation](https://apscheduler.readthedocs.io/)

---

## 🎉 Enjoy!

Your WhatsApp bot is now more powerful with:
- 🔐 Secure localStorage config
- 🤖 16 AI model options
- ⏰ Automated scheduling

Happy analyzing! 🚀
