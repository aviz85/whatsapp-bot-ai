import requests
import json
import logging
from datetime import datetime
from typing import List, Dict, Any
from config import settings
from models import OpenRouterRequest, OpenRouterResponse, PriorityReport


class OpenRouterClient:
    """Client for interacting with OpenRouter API"""
    
    def __init__(self):
        self.api_key = settings.openrouter_api_key
        self.model = settings.openrouter_model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.logger = logging.getLogger(__name__)
    
    def _create_analysis_prompt(self, conversation_summaries: List[Dict]) -> str:
        """
        Create a prompt for AI to analyze and prioritize conversations
        
        Args:
            conversation_summaries: List of conversation summaries
        
        Returns:
            Prompt string for the AI
        """
        conversations_text = json.dumps(conversation_summaries, ensure_ascii=False, indent=2)
        
        prompt = f"""
אתה עוזר אישי חכם לניהול הודעות ווצאפ. אנא אנלז את השיחות הפתוחות הבאות ודרג אותן לפי דחיפות.

שיחות פתוחות לניתוח:
{conversations_text}

אנא בצע את הפעולות הבאות:
1. זהה שיחות דחופות שדורשות תגובה מיידית (למשל: חירום, בקשות חשובות, שאלות שקשורות לעסק/עבודה)
2. זהה שיחות חשובות שדורשות תגובה בקרוב (למשל: שאלות אישיות, תיאום פגישות)
3. סווג את השאר כשיחות רגילות שניתן לענות עליהן מאוחר יותר

החזר תגובה בפורמט JSON הבא בלבד:
{{
    "urgent_conversations": [
        {{
            "chat_id": "מזהה צ'אט",
            "chat_name": "שם הצ'אט",
            "reason": "סיבה לדחיפות",
            "suggested_response": "הצעה לתגובה מתאימה"
        }}
    ],
    "important_conversations": [
        {{
            "chat_id": "מזהה צ'אט",
            "chat_name": "שם הצ'אט",
            "reason": "סיבה לחשיבות",
            "suggested_response": "הצעה לתגובה מתאימה"
        }}
    ],
    "normal_conversations": [
        {{
            "chat_id": "מזהה צ'אט",
            "chat_name": "שם הצ'אט",
            "reason": "סיבה לסיווג"
        }}
    ],
    "summary": "סיכום כללי של המצב והמלצות לפעולה",
    "total_conversations": מספר כולל של שיחות
}}

הערה: עבור "normal_conversations", אל תחזיר "suggested_response". תחזיר רק עבור שיחות דחופות וחשובות.
חשוב: החזר רק JSON תקין, בלי טקסט נוסף.
"""
        return prompt
    
    def analyze_conversations(self, conversation_summaries: List[Dict]) -> PriorityReport:
        """
        Send conversation summaries to OpenRouter for analysis and prioritization
        
        Args:
            conversation_summaries: List of conversation summaries to analyze
        
        Returns:
            PriorityReport with categorized conversations
        """
        if not conversation_summaries:
            return PriorityReport(
                urgent_conversations=[],
                important_conversations=[],
                normal_conversations=[],
                summary="לא נמצאו שיחות פתוחות לניתוח.",
                total_conversations=0
            )
        
        try:
            # Create the prompt
            prompt = self._create_analysis_prompt(conversation_summaries)
            
            # Prepare the request
            request_data = {
                "model": settings.openrouter_model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 4000,
                "temperature": 0.1
            }
            
            headers = {
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://whatsapp-bot.local",
                "X-Title": "WhatsApp Bot Assistant"
            }
            
            self.logger.info(f"Sending {len(conversation_summaries)} conversations to OpenRouter for analysis")
            
            # Make the API request
            response = requests.post(self.base_url, json=request_data, headers=headers)
            response.raise_for_status()
            
            response_data = response.json()
            
            # Extract the AI response
            if "choices" in response_data and len(response_data["choices"]) > 0:
                ai_response = response_data["choices"][0]["message"]["content"]
                
                # Parse the JSON response
                try:
                    import re
                    
                    # Technique 1: Clean markdown code blocks
                    clean_response = ai_response.strip()
                    if "```json" in clean_response:
                        # Extract content between ```json and ```
                        match = re.search(r'```json\s*(.*?)\s*```', clean_response, re.DOTALL)
                        if match:
                            clean_response = match.group(1)
                    elif "```" in clean_response:
                        # Extract content between ``` and ```
                        match = re.search(r'```\s*(.*?)\s*```', clean_response, re.DOTALL)
                        if match:
                            clean_response = match.group(1)
                    
                    # Technique 2: Find the first { and last }
                    json_start = clean_response.find('{')
                    json_end = clean_response.rfind('}')
                    
                    if json_start != -1:
                        # If we found a start but the end is missing or before the start
                        if json_end == -1 or json_end < json_start:
                            self.logger.warning("JSON seems truncated, attempting smart repair...")
                            clean_response = self._repair_json(clean_response[json_start:])
                        else:
                            clean_response = clean_response[json_start:json_end+1]
                    
                    # Try to parse
                    try:
                        analysis_result = json.loads(clean_response)
                    except json.JSONDecodeError as e1:
                        self.logger.warning(f"Standard JSON parse failed: {e1}")
                        
                        # Technique 3: Try to fix common JSON errors
                        try:
                            # Remove trailing commas
                            clean_response_fixed = re.sub(r',\s*([}\]])', r'\1', clean_response)
                            # Fix unescaped quotes
                            clean_response_fixed = re.sub(r'(?<=\w)"(?=\w)', '\\"', clean_response_fixed)
                            # Try smart repair again on the fixed version if it looks truncated
                            if not clean_response_fixed.endswith(('}', ']')):
                                clean_response_fixed = self._repair_json(clean_response_fixed)
                                
                            analysis_result = json.loads(clean_response_fixed)
                        except json.JSONDecodeError as e2:
                            self.logger.warning(f"Fix attempt failed: {e2}")
                            
                            # Technique 4: Try ast.literal_eval (handles Python dict syntax which is common from AI)
                            import ast
                            try:
                                self.logger.warning("Trying ast.literal_eval...")
                                # Replace JSON null/true/false with Python None/True/False
                                python_syntax = clean_response.replace('null', 'None').replace('true', 'True').replace('false', 'False')
                                analysis_result = ast.literal_eval(python_syntax)
                            except Exception as e3:
                                self.logger.error(f"All parsing attempts failed.")
                                self.logger.error(f"Original JSON error: {e1}")
                                self.logger.error(f"Fix attempt error: {e2}")
                                self.logger.error(f"AST error: {e3}")
                                
                                # Raise the original error as it's usually the most descriptive
                                raise ValueError(f"JSON Parse Error: {e1}")
                    
                    # Create PriorityReport object
                    report = PriorityReport(
                        urgent_conversations=analysis_result.get("urgent_conversations", []),
                        important_conversations=analysis_result.get("important_conversations", []),
                        normal_conversations=analysis_result.get("normal_conversations", []),
                        summary=analysis_result.get("summary", ""),
                        total_conversations=analysis_result.get("total_conversations", 0)
                    )
                    
                    self.logger.info(f"Successfully analyzed conversations: {len(report.urgent_conversations)} urgent, {len(report.important_conversations)} important, {len(report.normal_conversations)} normal")
                    
                    return report
                
                except Exception as e:
                    self.logger.error(f"Failed to parse AI response as JSON: {e}")
                    self.logger.error(f"Raw response: {ai_response}")
                    
                    # Fallback: Return empty report with error summary
                    return PriorityReport(
                        urgent_conversations=[],
                        important_conversations=[],
                        normal_conversations=[],
                        summary=f"שגיאה בפענוח תשובת ה-AI. התקבל תוכן לא תקין. (שגיאה: {str(e)})",
                        total_conversations=0
                    )
            
            else:
                raise ValueError("No valid response from OpenRouter")
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get analysis from OpenRouter: {e}")
            raise
    
    def generate_summary_report(self, report: PriorityReport) -> str:
        """
        Generate a human-readable summary report from the AI analysis
        
        Args:
            report: PriorityReport from AI analysis
        
        Returns:
            Formatted summary string
        """
        def format_phone_link(chat_id: str, chat_name: str) -> str:
            """Convert chat_id to WhatsApp link with phone number"""
            # Extract phone number from chat_id (remove @c.us or @g.us)
            phone = chat_id.replace('@c.us', '').replace('@g.us', '')
            
            # Check if it's a group chat
            if '@g.us' in chat_id:
                return f"• {chat_name} (קבוצה)"
            
            # Create WhatsApp link for personal chats
            wa_link = f"https://wa.me/{phone}"
            return f"• {chat_name} ({phone})\n  💬 {wa_link}"
        
        summary_lines = []
        summary_lines.append("📊 *דוח שיחות פתוחות*")
        summary_lines.append(f"📅 נוצר בתאריך: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        summary_lines.append(f"📈 סה\"כ שיחות פתוחות: {report.total_conversations}")
        summary_lines.append("")
        
        if report.urgent_conversations:
            summary_lines.append("🚨 *שיחות דחופות:*")
            for conv in report.urgent_conversations:
                summary_lines.append(format_phone_link(
                    conv.get('chat_id', ''), 
                    conv.get('chat_name', 'לא ידוע')
                ))
                summary_lines.append(f"  📌 סיבה: {conv.get('reason', '')}")
            summary_lines.append("")
        
        if report.important_conversations:
            summary_lines.append("⭐ *שיחות חשובות:*")
            for conv in report.important_conversations:
                summary_lines.append(format_phone_link(
                    conv.get('chat_id', ''), 
                    conv.get('chat_name', 'לא ידוע')
                ))
                summary_lines.append(f"  📌 סיבה: {conv.get('reason', '')}")
            summary_lines.append("")
        
        if report.normal_conversations:
            summary_lines.append("📝 *שיחות רגילות:*")
            for conv in report.normal_conversations[:3]:  # Show only first 3 normal conversations
                phone = conv.get('chat_id', '').replace('@c.us', '').replace('@g.us', '')
                summary_lines.append(f"• {conv.get('chat_name', 'לא ידוע')} ({phone})")
            if len(report.normal_conversations) > 3:
                summary_lines.append(f"• ועוד {len(report.normal_conversations) - 3} שיחות רגילות...")
            summary_lines.append("")
        
        summary_lines.append("📋 *סיכום:*")
        summary_lines.append(report.summary)
        
        return "\n".join(summary_lines)

    def _repair_json(self, json_str: str) -> str:
        """Attempt to repair truncated JSON by closing open brackets/braces"""
        stack = []
        in_string = False
        escape = False
        
        for char in json_str:
            if escape:
                escape = False
                continue
            if char == '\\':
                escape = True
                continue
            if char == '"':
                in_string = not in_string
                continue
            
            if not in_string:
                if char == '{':
                    stack.append('}')
                elif char == '[':
                    stack.append(']')
                elif char == '}' or char == ']':
                    if stack and stack[-1] == char:
                        stack.pop()
        
        # Close string if open
        if in_string:
            json_str += '"'
            
        # Close all open structures
        while stack:
            closer = stack.pop()
            json_str += closer
            
        return json_str
