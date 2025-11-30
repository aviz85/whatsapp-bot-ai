#!/usr/bin/env python
"""
Test sending a message to the configured user phone number
"""
import asyncio
import logging
from whatsapp_bot import bot
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_send_to_user():
    """Test sending a message to the user's configured phone number"""
    print("=" * 60)
    print("Testing Message Send to User Phone Number")
    print("=" * 60)
    
    test_message = f"""🧪 *בדיקת שליחה למספר המשתמש*

📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

✅ זוהי בדיקה שהמערכת שולחת הודעות למספר הנכון!

אם קיבלת הודעה זו, המערכת מוגדרת כראוי ודוחות הניתוח יישלחו אליך.

🎯 המספר המוגדר: [YOUR_PHONE_NUMBER]"""
    
    try:
        # Send message using the bot's method
        print(f"\n📤 Sending test message via bot...")
        result = await bot.send_custom_message(
            chat_id="YOUR_PHONE_NUMBER@c.us",  # Replace with your number
            message=test_message
        )
        
        print(f"\n✅ Message sent successfully!")
        print(f"   Result: {result}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = asyncio.run(test_send_to_user())
    
    if success:
        print("\n🎉 Test passed! Check your WhatsApp.")
    else:
        print("\n❌ Test failed!")
