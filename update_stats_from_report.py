#!/usr/bin/env python
"""
Update bot stats from the latest analysis report
"""
from whatsapp_bot import bot
from database import db

print("=" * 60)
print("Updating Bot Stats from Latest Report")
print("=" * 60)

# Get latest report
report = db.get_latest_analysis_report()

if report:
    print(f"\n✅ Found report with {report.get('total_conversations', 0)} conversations")
    
    # Update bot stats
    bot.stats.urgent_conversations = len(report.get('urgent_conversations', []))
    bot.stats.unanswered_conversations = report.get('total_conversations', 0)
    
    print(f"\n📊 Updated Stats:")
    print(f"   Urgent conversations: {bot.stats.urgent_conversations}")
    print(f"   Unanswered conversations: {bot.stats.unanswered_conversations}")
    print(f"   Total messages: {bot.stats.total_messages}")
    print(f"   Active chats: {bot.stats.active_chats}")
    
    print("\n✅ Stats updated successfully!")
    print("   Refresh the dashboard to see the changes")
else:
    print("\n❌ No report found in database")
    print("   Run an analysis first!")

print("=" * 60)
