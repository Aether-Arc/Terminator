import json
from langchain_openai import ChatOpenAI
from langchain_core.utils.json import parse_json_markdown # 🚀 The bulletproof parser!
from config import CLOUD_MODEL, OLLAMA_BASE_URL, OPENAI_API_KEY
from tools.system_tools import swarm_tools

class CommsAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model=CLOUD_MODEL, base_url=OLLAMA_BASE_URL, api_key=OPENAI_API_KEY, temperature=0.2)

    async def draft_communications(self, event_data, schedule, specifics):
        """
        Runs during the Map-Reduce Execution Phase. 
        Drafts both Email and WhatsApp but DOES NOT SEND THEM.
        """
        prompt = f"""
        You are the Communications Director for an event. 
        Event Context: {json.dumps(event_data)}
        Schedule: {json.dumps(schedule)}
        Task: "{specifics}"
        
        Write the copy for both Email and WhatsApp channels. Keep WhatsApp short and punchy. Keep Email professional.
        
        Return ONLY valid JSON format:
        {{
            "use_email": true,
            "email_subject": "Subject here",
            "email_body": "Body here",
            "use_whatsapp": true,
            "whatsapp_body": "Body here",
            "status": "DRAFTED"
        }}
        """
        
        try:
            res = await self.llm.ainvoke(prompt)
            # 🚀 Cleanly parses the JSON, ignoring any conversational LLM filler!
            strategy = parse_json_markdown(res.content)
            strategy["recipient"] = "All Participants"
            return strategy
            
        except Exception as e:
            print(f"[*] CommsAgent Error: Failed to parse LLM JSON: {e}")
            return {
                "use_email": True, "email_subject": "Event Update", "email_body": "Drafting failed.",
                "use_whatsapp": False, "whatsapp_body": "", "status": "ERROR"
            }