import os
import re
from twilio.rest import AsyncClient # 🚀 IMPORT THE ASYNC CLIENT

# 🚀 It is now an async function!
async def send_whatsapp_blast(contacts: list[dict], message: str) -> list[str]:
    """Sends an asynchronous REAL WhatsApp message to all contacts via Twilio."""
    
    # 1. PULL FROM ENVIRONMENT VARIABLES (Security)
    account_sid = "ACe1abaa917bd7761d0305399c3398f0d7"
    auth_token = "2576855951c09b5e679c8608b19b9e2a"
    twilio_number = "whatsapp:+14155238886" # Your Twilio Sandbox Number
    
    # 2. USE ASYNC CLIENT (Prevents FastAPI from freezing)
    client = AsyncClient(account_sid, auth_token)
    logs = []
    
    for contact in contacts:
        raw_phone = contact.get("phone")
        name = contact.get("name", "Participant")
        
        if raw_phone:
            # 3. CLEAN THE PHONE NUMBER (Strips spaces, dashes, parentheses)
            # Example: "(123) 456-7890" becomes "1234567890"
            clean_phone = re.sub(r'\D', '', str(raw_phone))
            
            # Ensure it has a '+' prefix (Assuming US/Canada '+1' if missing for testing)
            # You might need to adjust this depending on your target country codes
            if not clean_phone.startswith('+'):
                # Just an example: if it's 10 digits, assume US +1. Otherwise just prepend +
                if len(clean_phone) == 10:
                    clean_phone = f"+1{clean_phone}"
                else:
                    clean_phone = f"+{clean_phone}"

            formatted_message = f"Hi {name},\n\n{message}"
            
            try:
                # 🚀 AWAIT THE MESSAGE CREATION
                msg = await client.messages.create(
                  from_=twilio_number,
                  body=formatted_message,
                  to=f'whatsapp:{clean_phone}'
                )
                logs.append(f"✅ REAL WhatsApp sent to {name} ({clean_phone}) - ID: {msg.sid}")
            except Exception as e:
                logs.append(f"❌ Failed to WhatsApp {name} ({clean_phone}): {e}")
                
    return logs