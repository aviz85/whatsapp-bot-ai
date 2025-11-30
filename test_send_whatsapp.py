#!/usr/bin/env python
"""
Test script to send a WhatsApp message to verify Green API integration
"""
import logging
from green_api_client import GreenAPIClient
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_send_message():
    """Test sending a message via Green API"""
    print("=" * 60)
    print("Testing WhatsApp Message Sending")
    print("=" * 60)
    
    # Test sending message
    phone_number = "YOUR_PHONE_NUMBER_HERE"  # Replace with your phone number
    chat_id = f"{phone_number}@c.us"
    
    # Test message
    test_message = f"""🤖 *בדיקת מערכת WhatsApp Bot*

📅 תאריך: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

✅ המערכת פועלת כראוי!

זוהי הודעת בדיקה אוטומטית מהבוט שלך.
אם קיבלת הודעה זו, המערכת מחוברת בהצלחה ל-Green API.

🚀 הבוט מוכן לשימוש!"""
    
    try:
        # Create Green API client
        print(f"\n📱 Creating Green API client...")
        client = GreenAPIClient()
        
        print(f"   API URL: {client.base_url}")
        print(f"   Instance ID: {client.id_instance}")
        print(f"   Token: {client.token_instance[:10]}...")
        
        # Test account connection first
        print(f"\n🔍 Testing account connection...")
        account_info = client.get_account_info()
        print(f"   ✅ Account connected: {account_info.get('phone', 'Unknown')}")
        print(f"   Status: {account_info.get('stateInstance', 'Unknown')}")
        
        # Send test message
        print(f"\n📤 Sending test message to {phone_number}...")
        print(f"   Chat ID: {chat_id}")
        print(f"\n   Message content:")
        print("   " + "-" * 50)
        for line in test_message.split('\n'):
            print(f"   {line}")
        print("   " + "-" * 50)
        
        result = client.send_message(chat_id, test_message)
        
        print(f"\n✅ Message sent successfully!")
        print(f"   Message ID: {result.get('idMessage', 'Unknown')}")
        print(f"   Full response: {result}")
        
        print("\n" + "=" * 60)
        print("🎉 Test completed successfully!")
        print("=" * 60)
        print(f"\n📱 Check your WhatsApp at {phone_number}")
        print("   You should receive the test message shortly.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error sending message: {e}")
        import traceback
        print("\nFull traceback:")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = test_send_message()
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Tests failed!")
