# VS Code Debug Configuration Guide

## 🐛 Available Debug Configurations

Your `.vscode/launch.json` includes 8 debug configurations for different scenarios:

---

## 1. **Python: WhatsApp Bot (Main)** 🚀
**Best for**: Normal development and debugging

**What it does**:
- Launches the main FastAPI application
- Opens dashboard at http://localhost:8000
- Debugs only your code (not libraries)
- Uses integrated terminal

**How to use**:
1. Press `F5` or click "Run and Debug"
2. Select "Python: WhatsApp Bot (Main)"
3. Set breakpoints in your code
4. Open http://localhost:8000 in browser

**Use when**:
- Testing the main application
- Debugging API endpoints
- Working on dashboard features

---

## 2. **Python: WhatsApp Bot (Dev Mode)** 🔧
**Best for**: Deep debugging including libraries

**What it does**:
- Same as Main but with `justMyCode: false`
- Steps into library code (FastAPI, Pydantic, etc.)
- Sets DEBUG=True environment variable
- Full debugging capability

**How to use**:
1. Select "Python: WhatsApp Bot (Dev Mode)"
2. Press `F5`
3. Can step into any code, including dependencies

**Use when**:
- Debugging library integration issues
- Understanding how FastAPI works internally
- Tracing complex errors through dependencies

---

## 3. **Python: Test Config** ⚙️
**Best for**: Testing configuration loading

**What it does**:
- Runs `test_config.py`
- Validates environment variables
- Checks API connections

**How to use**:
1. Open `test_config.py`
2. Set breakpoints if needed
3. Select "Python: Test Config"
4. Press `F5`

**Use when**:
- Verifying .env file is correct
- Testing API key validity
- Debugging configuration issues

---

## 4. **Python: Test Send WhatsApp** 📱
**Best for**: Testing WhatsApp message sending

**What it does**:
- Runs `test_send_whatsapp.py`
- Tests Green API connection
- Sends test message

**How to use**:
1. Update phone number in `test_send_whatsapp.py`
2. Set breakpoints if needed
3. Select "Python: Test Send WhatsApp"
4. Press `F5`

**Use when**:
- Testing Green API integration
- Verifying message sending works
- Debugging WhatsApp connection issues

---

## 5. **Python: Test Send Report** 📊
**Best for**: Testing report generation and sending

**What it does**:
- Runs `test_send_report.py`
- Tests AI analysis
- Sends formatted report

**How to use**:
1. Select "Python: Test Send Report"
2. Press `F5`
3. Check WhatsApp for report

**Use when**:
- Testing AI analysis
- Debugging report formatting
- Verifying OpenRouter integration

---

## 6. **Python: Check Status** 🔍
**Best for**: Checking system status

**What it does**:
- Runs `check_status.py`
- Checks all API connections
- Validates configuration

**How to use**:
1. Select "Python: Check Status"
2. Press `F5`
3. Review output

**Use when**:
- Quick system health check
- Verifying all services are working
- Debugging connection issues

---

## 7. **Python: Current File** 📄
**Best for**: Debugging any Python file

**What it does**:
- Runs whatever file is currently open
- Flexible debugging for any script
- Uses current file's context

**How to use**:
1. Open any Python file
2. Select "Python: Current File"
3. Press `F5`

**Use when**:
- Testing new scripts
- Debugging utility files
- Quick one-off debugging

---

## 8. **Python: Attach to FastAPI** 🔌
**Best for**: Remote debugging of running server

**What it does**:
- Attaches to already running FastAPI server
- Requires debugpy server running on port 5678
- Allows debugging without restarting

**How to use**:
1. Start server with debugpy:
   ```python
   import debugpy
   debugpy.listen(("0.0.0.0", 5678))
   debugpy.wait_for_client()
   ```
2. Select "Python: Attach to FastAPI"
3. Press `F5`

**Use when**:
- Debugging production-like environment
- Server is already running
- Need to debug without restart

---

## 🎯 Quick Start Guide

### First Time Setup:

1. **Install Python Extension**
   - Open VS Code
   - Install "Python" extension by Microsoft

2. **Install debugpy**
   ```bash
   pip install debugpy
   ```

3. **Open Debug Panel**
   - Press `Ctrl+Shift+D` (Windows/Linux)
   - Press `Cmd+Shift+D` (Mac)
   - Or click Debug icon in sidebar

4. **Select Configuration**
   - Use dropdown at top of Debug panel
   - Choose appropriate configuration

5. **Start Debugging**
   - Press `F5`
   - Or click green play button

---

## 🔧 Common Debugging Tasks

### Debug Main Application:
```
1. Select: "Python: WhatsApp Bot (Main)"
2. Press: F5
3. Open: http://localhost:8000
4. Set breakpoints in main.py, whatsapp_bot.py, etc.
```

### Debug API Endpoint:
```
1. Open file with endpoint (e.g., main.py)
2. Set breakpoint in endpoint function
3. Press F5
4. Trigger endpoint from browser/Postman
5. Debugger stops at breakpoint
```

### Debug Analysis Flow:
```
1. Set breakpoints in:
   - whatsapp_bot.py (analyze_and_report)
   - message_analyzer.py (analyze_conversations)
   - openrouter_client.py (analyze_conversations)
2. Press F5
3. Click "Analyze Messages" in dashboard
4. Step through code with F10/F11
```

### Debug Cron Job:
```
1. Open cron_scheduler.py
2. Set breakpoint in run_scheduled_analysis
3. Manually trigger or wait for schedule
4. Debug when triggered
```

---

## ⌨️ Keyboard Shortcuts

| Action | Windows/Linux | Mac |
|--------|---------------|-----|
| Start/Continue | `F5` | `F5` |
| Step Over | `F10` | `F10` |
| Step Into | `F11` | `F11` |
| Step Out | `Shift+F11` | `Shift+F11` |
| Stop | `Shift+F5` | `Shift+F5` |
| Restart | `Ctrl+Shift+F5` | `Cmd+Shift+F5` |
| Toggle Breakpoint | `F9` | `F9` |

---

## 🎨 Breakpoint Tips

### Conditional Breakpoints:
```python
# Right-click breakpoint → Edit Breakpoint → Add condition
# Example: chat_id == "972501234567@c.us"
```

### Logpoints:
```python
# Right-click → Add Logpoint
# Example: Message: {message.text_message}
```

### Hit Count:
```python
# Right-click → Edit Breakpoint → Hit Count
# Example: Break on 5th hit
```

---

## 🐛 Debugging Best Practices

### 1. Start Simple
- Use "Python: WhatsApp Bot (Main)" first
- Add breakpoints strategically
- Don't step through everything

### 2. Use Watch Expressions
- Add variables to Watch panel
- Monitor values in real-time
- Example: `bot.stats`, `analysis_progress`

### 3. Inspect Variables
- Hover over variables
- Use Debug Console for expressions
- Check locals/globals

### 4. Use Debug Console
```python
# Type expressions while debugging:
len(messages)
config.green_api_id_instance
bot.get_database_stats()
```

### 5. Log Strategically
```python
import logging
logger = logging.getLogger(__name__)
logger.debug(f"Processing {len(messages)} messages")
```

---

## 🔍 Common Issues

### Issue: Breakpoint Not Hit
**Solution**:
- Check file is saved
- Verify code path is executed
- Use `justMyCode: false` if in library

### Issue: Can't See Variables
**Solution**:
- Check scope (local vs global)
- Use Watch panel
- Type in Debug Console

### Issue: Server Won't Start
**Solution**:
- Check port 8000 is free
- Verify .env file exists
- Check Python interpreter

### Issue: Import Errors
**Solution**:
- Verify PYTHONPATH in launch.json
- Check virtual environment
- Install requirements.txt

---

## 📚 Additional Resources

- [VS Code Python Debugging](https://code.visualstudio.com/docs/python/debugging)
- [debugpy Documentation](https://github.com/microsoft/debugpy)
- [FastAPI Debugging](https://fastapi.tiangolo.com/tutorial/debugging/)

---

## 🎉 Quick Reference

**Most Used Configurations:**
1. **Main** - Normal development
2. **Dev Mode** - Deep debugging
3. **Current File** - Quick tests

**Most Used Shortcuts:**
- `F5` - Start
- `F10` - Step over
- `F11` - Step into
- `F9` - Toggle breakpoint

**Most Useful Panels:**
- Variables - See current values
- Watch - Monitor expressions
- Call Stack - See execution path
- Debug Console - Run code

---

**Happy Debugging! 🐛✨**
