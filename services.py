import json
import os
from typing import Optional, List
from datetime import datetime
from dateutil import parser
import ollama
from models import SuppressionInfo
from config import config

class SuppressionService:
    def __init__(self):
        self.suppressed_emails_data = self._load_suppressed_emails()
    
    def _load_suppressed_emails(self) -> List[SuppressionInfo]:
        """Load suppressed emails data from JSON file"""
        try:
            if not os.path.exists(config.SUPPRESSED_EMAILS_JSON_PATH):
                raise FileNotFoundError(f"Suppressed emails file not found: {config.SUPPRESSED_EMAILS_JSON_PATH}")
            
            with open(config.SUPPRESSED_EMAILS_JSON_PATH, 'r') as file:
                data = json.load(file)
                
            suppressed_emails = []
            for item in data.get("SuppressedDestinationSummaries", []):
                suppressed_emails.append(SuppressionInfo(
                    email_address=item["EmailAddress"],
                    reason=item["Reason"],
                    last_update_time=item["LastUpdateTime"]
                ))
            
            return suppressed_emails
        except Exception as e:
            print(f"Error loading suppressed emails data: {e}")
            return []
    
    def check_email_suppression(self, email: str) -> Optional[SuppressionInfo]:
        """Check if an email is suppressed"""
        for suppressed_email in self.suppressed_emails_data:
            if suppressed_email.email_address.lower() == email.lower():
                return suppressed_email
        return None
    
    def _format_datetime_human_readable(self, iso_datetime: str) -> str:
        """Convert ISO datetime to human readable format with timezone"""
        try:
            dt = parser.parse(iso_datetime)
            return dt.strftime("%B %d, %Y at %I:%M %p UTC")
        except Exception:
            return iso_datetime
    
    def _get_reason_explanation(self, reason: str) -> str:
        """Get human readable explanation for suppression reason"""
        reason_map = {
            "COMPLAINT": "the recipient marked emails from this sender as spam or complained about receiving them",
            "BOUNCE": "emails to this address consistently bounce back, indicating the email address may be invalid or the mailbox is full",
            "UNSUBSCRIBE": "the recipient has unsubscribed from receiving emails",
            "REPUTATION": "the sender's reputation has been negatively affected due to poor email practices"
        }
        return reason_map.get(reason.upper(), f"the email was suppressed due to {reason.lower()}")

class OllamaService:
    def __init__(self):
        self.client = ollama.Client(host=config.OLLAMA_BASE_URL)
        self.model = config.OLLAMA_MODEL
    
    def generate_human_explanation(self, email: str, reason: str, last_update_time: str, 
                                 formatted_time: str, reason_explanation: str) -> str:
        """Generate human-readable explanation using Ollama"""
        prompt = f"""You are an email suppression status assistant. Provide a clear, concise explanation in 1-2 sentences.

Email: {email}
Status: Suppressed
Reason: {reason}
Last Updated: {formatted_time}
Reason Explanation: {reason_explanation}

Write a professional explanation that combines all this information into a natural, human-readable response. Do not include any additional text, headers, formatting, thinking process, or reasoning - just provide the final explanation directly."""

        try:
            messages = [
                {
                    'role': 'user',
                    'content': prompt,
                }
            ]
            
            # Use think=False to disable thinking mode for faster responses
            response = self.client.chat(
                model=self.model,
                messages=messages,
                stream=False,
                think=False
            )
            
            # Clean the response to remove any thinking tags or unwanted content
            content = response['message']['content'].strip()
            
            # Remove thinking tags if they appear
            import re
            content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
            content = re.sub(r'<thinking>.*?</thinking>', '', content, flags=re.DOTALL)
            
            # Clean up any extra whitespace
            content = ' '.join(content.split())
            
            return content
        
        except Exception as e:
            print(f"Error generating explanation with Ollama: {e}")
            # Fallback explanation
            return f"The email address {email} is suppressed because {reason_explanation}. This suppression was last updated on {formatted_time}."
