import os
import re
import asyncio
from twilio.rest import Client # 🚀 USE STANDARD CLIENT

async def send_whatsapp_blast(contacts: list[dict], message: str) -> list[str]:
    """Sends an asynchronous REAL WhatsApp message to all contacts via Twilio."""
    
    account_sid = os.getenv("TWILIO_ACCOUNT_SID", "your_fallback_sid_here")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN", "your_fallback_token_here")
    twilio_number = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
    
    # 1. Initialize the standard client
    client = Client(account_sid, auth_token)
    logs = []
    
    for contact in contacts:
        raw_phone = contact.get("phone")
        name = contact.get("name", "Participant")
        
        if raw_phone:
            clean_phone = re.sub(r'\D', '', str(raw_phone))
            
            if not clean_phone.startswith('+'):
                if len(clean_phone) == 10:
                    clean_phone = f"+1{clean_phone}"
                else:
                    clean_phone = f"+{clean_phone}"

            formatted_message = f"Hi {name},\n\n{message}"
            
            try:
                # 🚀 2. THE FIX: Wrap the synchronous Twilio call in asyncio.to_thread
                # This perfectly bridges the gap, allowing FastAPI to remain unblocked!
                msg = await asyncio.to_thread(
                    client.messages.create,
                    from_=twilio_number,
                    body=formatted_message,
                    to=f'whatsapp:{clean_phone}'
                )
                logs.append(f"✅ REAL WhatsApp sent to {name} ({clean_phone}) - ID: {msg.sid}")
            except Exception as e:
                logs.append(f"❌ Failed to WhatsApp {name} ({clean_phone}): {e}")
                
    return logs