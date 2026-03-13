import os
from twilio.rest import Client

def send_whatsapp_blast(contacts: list[dict], message: str) -> list[str]:
    """Sends a REAL WhatsApp message to all contacts via Twilio."""
    
    # ⚠️ Replace these with your actual Twilio Sandbox credentials
    account_sid = "ACe1abaa917bd7761d0305399c3398f0d7"
    auth_token = "2576855951c09b5e679c8608b19b9e2a"
    twilio_number = "whatsapp:+14155238886" # Your Twilio Sandbox Number
    
    client = Client(account_sid, auth_token)
    logs = []
    
    for contact in contacts:
        phone = contact.get("phone")
        name = contact.get("name", "Participant")
        
        if phone:
            # Twilio requires the E.164 format and the 'whatsapp:' prefix
            # E.g., 'whatsapp:+1234567890'
            formatted_message = f"Hi {name},\n\n{message}"
            
            try:
                msg = client.messages.create(
                  from_=twilio_number,
                  body=formatted_message,
                  to=f'whatsapp:{phone}'
                )
                logs.append(f"✅ REAL WhatsApp sent to {name} ({phone}) - ID: {msg.sid}")
            except Exception as e:
                logs.append(f"❌ Failed to WhatsApp {name}: {e}")
                
    return logs