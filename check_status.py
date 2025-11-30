#!/usr/bin/env python
"""
Check current bot status and database
"""
import asyncio
from whatsapp_bot import bot
from database import db

async def check_status():
    print("=" * 60)
    print("Checking Bot Status and Database")
    print("=" * 60)
    
    # Check database stats
    print("\n📊 Database Statistics:")
    try:
        stats = bot.get_database_stats()
        print(f"   Total messages in DB: {stats.get('total_messages', 0)}")
        print(f"   Total chats: {stats.get('total_chats', 0)}")
        print(f"   Date range: {stats.get('date_range', 'N/A')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Check latest analysis report
    print("\n📋 Latest Analysis Report:")
    try:
        report = db.get_latest_analysis_report()
        if report:
            print(f"   ✅ Report found!")
            print(f"   Total conversations: {report.get('total_conversations', 0)}")
            print(f"   Urgent: {len(report.get('urgent_conversations', []))}")
            print(f"   Important: {len(report.get('important_conversations', []))}")
            print(f"   Normal: {len(report.get('normal_conversations', []))}")
            
            if report.get('urgent_conversations'):
                print("\n   🚨 Urgent conversations:")
                for conv in report['urgent_conversations'][:3]:
                    print(f"      - {conv.get('chat_name', 'Unknown')}: {conv.get('reason', 'N/A')}")
        else:
            print("   ⚠️ No analysis report found in database")
            print("   Run an analysis first!")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Check bot stats
    print("\n📈 Bot Statistics:")
    try:
        print(f"   Total messages: {bot.stats.total_messages}")
        print(f"   Unanswered conversations: {bot.stats.unanswered_conversations}")
        print(f"   Urgent conversations: {bot.stats.urgent_conversations}")
        print(f"   Active chats: {bot.stats.active_chats}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(check_status())
