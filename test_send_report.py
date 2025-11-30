#!/usr/bin/env python
"""
Test script to verify the send_report functionality
"""
import asyncio
import logging
from models import PriorityReport
from openrouter_client import OpenRouterClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_generate_summary_report():
    """Test the generate_summary_report function"""
    print("=" * 60)
    print("Testing generate_summary_report function")
    print("=" * 60)
    
    # Create a mock priority report
    test_report = PriorityReport(
        urgent_conversations=[
            {
                "chat_id": "972501234567@c.us",
                "chat_name": "אבי כהן",
                "reason": "בקשה דחופה לפגישה היום",
                "suggested_response": "שלום אבי, אני זמין להיפגש היום אחר הצהריים"
            }
        ],
        important_conversations=[
            {
                "chat_id": "972509876543@c.us",
                "chat_name": "שרה לוי",
                "reason": "שאלה חשובה לגבי פרויקט",
                "suggested_response": "שלום שרה, אענה לך בהקדם"
            }
        ],
        normal_conversations=[
            {
                "chat_id": "972505555555@c.us",
                "chat_name": "דוד ישראלי",
                "reason": "שיחה כללית",
                "suggested_response": "שלום דוד"
            }
        ],
        total_conversations=3,
        summary="נמצאו 3 שיחות פתוחות: 1 דחופה, 1 חשובה, 1 רגילה"
    )
    
    try:
        # Create OpenRouter client
        client = OpenRouterClient()
        
        # Generate report
        print("\nGenerating summary report...")
        formatted_report = client.generate_summary_report(test_report)
        
        print("\n" + "=" * 60)
        print("GENERATED REPORT:")
        print("=" * 60)
        print(formatted_report)
        print("=" * 60)
        
        print(f"\n✅ Report generated successfully!")
        print(f"Report length: {len(formatted_report)} characters")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error generating report: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = test_generate_summary_report()
    
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Tests failed!")
