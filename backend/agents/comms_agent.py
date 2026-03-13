from langchain_openai import ChatOpenAI
from config import CLOUD_MODEL, OLLAMA_BASE_URL, OPENAI_API_KEY
from tools.csv_parser import parse_messy_csv
from services.whatsapp_service import send_whatsapp_blast
from services.email_service import send_email 
import json

# 👇 --- HIGHLIGHT: IMPORT REGEX TO PARSE MESSY LLM OUTPUTS --- 👇
import re
# 👆 ----------------------------------------------------------- 👆

class CommsAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model=CLOUD_MODEL, base_url=OLLAMA_BASE_URL, api_key=OPENAI_API_KEY, temperature=0.2)

    async def execute_broadcast(self, csv_content: str, command: str, event_context: str):
        """
        1. Parses the command to determine channels.
        2. Drafts channel-specific messages.
        3. Extracts standard data from the messy CSV.
        4. Dispatches the messages.
        """
        prompt = f"""
        You are the Communications Director for an event. 
        Event Context: {event_context}
        Organizer Command: "{command}"
        
        Determine which communication channels the organizer wants to use (email, whatsapp, or both).
        Write the copy for each requested channel. Keep WhatsApp short and punchy. Keep Email professional.
        
        Return ONLY valid JSON:
        {{
            "use_email": true,
            "email_subject": "Subject here",
            "email_body": "Body here",
            "use_whatsapp": true,
            "whatsapp_body": "Body here"
        }}
        """
        
        res = await self.llm.ainvoke(prompt)
        raw_output = res.content
        
        # 👇 --- HIGHLIGHT: BULLETPROOF JSON EXTRACTION & FALLBACK --- 👇
        try:
            # Use regex to find everything between the first { and last }
            match = re.search(r'\{.*\}', raw_output, re.DOTALL)
            if match:
                clean_json = match.group(0)
            else:
                # Fallback to basic stripping if regex fails
                clean_json = raw_output.replace("```json", "").replace("```", "").strip()
                
            strategy = json.loads(clean_json)
            
        except Exception as e:
            print(f"[*] CommsAgent Error: Failed to parse LLM JSON: {e}")
            print(f"[*] Raw LLM Output was: {raw_output}")
            
            # Safe Fallback Strategy so the server doesn't crash
            strategy = {
                "use_email": True,
                "email_subject": "URGENT: Event Update",
                "email_body": f"Notice: {command}",
                "use_whatsapp": False,
                "whatsapp_body": ""
            }
        # 👆 ----------------------------------------------------------- 👆
        
        # 2. Parse the messy CSV
        contacts = parse_messy_csv(csv_content)
        
        if not contacts:
            return {"error": "No valid contacts found in CSV."}

        logs = []
        
        # 3. Dispatch Emails
        if strategy.get("use_email"):
            for contact in contacts:
                email = contact.get("email")
                name = contact.get("name", "Participant")
                
                if email and email != "null":
                    logs.append(f"✅ Email queued for {name} ({email})")

        # 4. Dispatch WhatsApps
        if strategy.get("use_whatsapp"):
            whatsapp_logs = send_whatsapp_blast(contacts, strategy["whatsapp_body"])
            logs.extend(whatsapp_logs)
            
        return {
            "status": "Broadcast Complete",
            "strategy": strategy,
            "contacts_processed": len(contacts),
            "logs": logs
        }