# 🤖 WhatsApp Bot with AI Analysis

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Smart WhatsApp bot that automatically analyzes incoming messages, identifies unanswered conversations, prioritizes them using AI, and sends automated reports.

## ✨ Features

### 🔐 **localStorage-Based Configuration**
- API keys stored securely in browser (not on server)
- Multi-user support with individual configurations
- No server restart needed for config changes

### 🤖 **16 AI Models Available**
Choose from multiple AI providers:
- **Claude** (Anthropic): Opus 4.5, Sonnet 3.7, Sonnet 3.5
- **Gemini** (Google): 3 Pro, 2.5 Pro, 2.5 Flash, Flash 1.5
- **GPT** (OpenAI): 5.1, 5.1 Chat, 5, 4o, 4 Turbo
- **Grok** (xAI): 4.1 Fast, 4, 3, 3 Mini

### ⏰ **Cron Job Scheduler**
- Automated analysis at scheduled times
- Predefined templates (daily, hourly, etc.)
- Custom cron expressions
- Real-time status monitoring

### 📊 **Smart Analysis**
- Automatically detects unanswered conversations
- AI-powered urgency prioritization
- Groups messages by chat
- Filters group vs private messages
- Sends formatted reports to WhatsApp

### 🎨 **Beautiful Dashboard**
- Real-time statistics
- Progress tracking
- Tabbed settings interface
- Hebrew RTL support
- Responsive design

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- Green API account ([sign up](https://green-api.com/))
- OpenRouter API key ([get key](https://openrouter.ai/))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/whatsapp-bot.git
cd whatsapp-bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure (Optional - can also configure via dashboard)**
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. **Run the application**
```bash
python main.py
```

5. **Open dashboard**
```
http://localhost:8000
```

6. **Configure via Dashboard**
- Click "⚙️ הגדרות" (Settings)
- Enter your API keys in the "🔑 API Keys" tab
- Choose AI model in "🤖 AI Model" tab
- Setup cron schedule in "⏰ Cron Schedule" tab (optional)
- Click "💾 שמור הגדרות" (Save Settings)

## 📖 Documentation

- **[NEW_FEATURES.md](NEW_FEATURES.md)** - Comprehensive feature guide
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Technical details
- **[.gemini/app_review.md](.gemini/app_review.md)** - Complete application review

## 🔧 Configuration

### Environment Variables (.env)
```env
# Green API Configuration
GREEN_API_URL=https://api.green-api.com
GREEN_API_ID_INSTANCE=your_instance_id
GREEN_API_TOKEN_INSTANCE=your_token

# User Configuration
USER_PHONE_NUMBER=972501234567

# OpenRouter Configuration
OPENROUTER_API_KEY=sk-or-v1-your-key
OPENROUTER_MODEL=openai/gpt-4o

# Application Configuration
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=True

# Cron Configuration
CRON_ENABLED=False
CRON_SCHEDULE=0 9 * * *
```

**Note:** You can also configure everything via the dashboard (recommended for security).

## 📊 API Endpoints

### Main Endpoints
- `GET /` - Dashboard UI
- `POST /api/analyze` - Trigger message analysis
- `GET /api/status` - Get bot statistics
- `GET /api/messages` - Get recent messages
- `GET /api/models` - Get available AI models
- `GET /api/cron/status` - Get cron scheduler status
- `POST /api/cron/update` - Update cron schedule

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         FastAPI Web Server              │
│         (main.py)                       │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
┌─────────────┐  ┌──────────────┐
│ WhatsApp    │  │  Database    │
│ Bot Service │  │  Manager     │
└──────┬──────┘  └──────┬───────┘
       │                │
   ┌───┴────┬──────────┴┐
   │        │           │
   ▼        ▼           ▼
┌────────┐ ┌─────────┐ ┌──────────┐
│ Green  │ │OpenRouter│ │ SQLite   │
│ API    │ │ Client  │ │ Database │
└────────┘ └─────────┘ └──────────┘
```

## 🔐 Security

- API keys stored in browser localStorage (not on server)
- .env file excluded from git
- No hardcoded credentials in code
- HTTPS recommended for production
- Regular key rotation recommended

## 🎯 Use Cases

- **Customer Support**: Never miss urgent customer messages
- **Sales Management**: Prioritize hot leads automatically
- **Personal Use**: Manage multiple conversations efficiently
- **Small Business**: Automated message monitoring

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI
- **Database**: SQLite
- **AI**: OpenRouter (GPT, Claude, Gemini, Grok)
- **WhatsApp**: Green API
- **Scheduler**: APScheduler
- **Frontend**: HTML, JavaScript, Jinja2

## 📝 Example Workflows

### Daily Morning Report
```
Schedule: 0 9 * * *
Model: GPT-4o
Result: Analyzes last 24 hours every morning at 9 AM
```

### High-Quality Analysis
```
Schedule: 0 12 * * *
Model: Claude Opus 4.5
Result: Best quality analysis at noon daily
```

### Fast & Frequent
```
Schedule: */30 * * * *
Model: Gemini Flash 2.5
Result: Quick analysis every 30 minutes
```

## 🐛 Troubleshooting

### Config Not Saving?
- Check browser console for errors
- Ensure localStorage is enabled
- Try different browser

### Cron Not Running?
- Verify cron expression is valid
- Check server logs
- Ensure server is running continuously

### API Calls Failing?
- Verify API keys in settings
- Check Green API account status
- Test with different AI model

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Green API](https://green-api.com/) - WhatsApp integration
- [OpenRouter](https://openrouter.ai/) - AI model access
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [APScheduler](https://apscheduler.readthedocs.io/) - Task scheduling

## 📞 Support

For issues or questions:
1. Check the [documentation](NEW_FEATURES.md)
2. Review [troubleshooting guide](#-troubleshooting)
3. Open an issue on GitHub

## 🎉 Features Roadmap

- [ ] Multi-language support
- [ ] Webhook integration
- [ ] Export reports to PDF/Excel
- [ ] Sentiment analysis
- [ ] Auto-responses with templates
- [ ] Mobile app
- [ ] Team collaboration features

---

**Made with ❤️ for better WhatsApp management**
