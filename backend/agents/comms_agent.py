import json
import re
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langgraph.prebuilt import create_react_agent # 🚀 Required for Web Search abilities
from langchain_core.utils.json import parse_json_markdown
from config import CLOUD_MODEL, OLLAMA_BASE_URL, OPENAI_API_KEY
from tools.system_tools import swarm_tools

from config import get_resilient_llm

class CommsOutput(BaseModel):
    use_email: bool = Field(description="Whether to send an email")
    email_subject: str = Field(description="The email subject line")
    email_body: str = Field(description="The full email body")
    use_whatsapp: bool = Field(description="Whether to send a WhatsApp")
    whatsapp_body: str = Field(description="The short WhatsApp message")
    status: str = Field(default="DRAFTED")
    recipient: str = Field(default="All Participants")

class CommsAgent:
    def __init__(self):
        # We use a slightly higher temperature (0.4) here to allow for creative, engaging copywriting
        self.llm = get_resilient_llm(temperature=0.4)

        # 🚀 THE UPGRADE: We bind the web search tools so the agent can browse the internet!
        self.agent_executor = create_react_agent(self.llm, swarm_tools)
        self.formatter_llm = get_resilient_llm(temperature=0).with_structured_output(CommsOutput)

    async def draft_communications(self, event_data, schedule, specifics):
        """
        Runs during the Map-Reduce Execution Phase. 
        Uses Web Search to gather real-world context before drafting.
        """
        event_name = event_data.get("name", "The Event")
        location = event_data.get("location", "the venue")
        theme = event_data.get("theme", "general event")
        
        prompt = f"""
        You are the Elite Communications Director for an event. 
        
        EVENT CONTEXT:
        - Name: {event_name}
        - Location: {location}
        - Theme/Type: {theme}
        - Full Data: {json.dumps(event_data)}
        
        SCHEDULE: {json.dumps(schedule)}
        
        SPECIFIC TASK: "{specifics}"
        
        🔥 MANDATORY RESEARCH PROTOCOL:
        1. You MUST use the 'web_search' tool FIRST. Search the internet for current trends, buzzwords, or recent news regarding "{theme} events in {location}", or look up "{event_name}" directly if it's a known brand.
        2. Do NOT draft generic copy. Incorporate the flavor, local context, and insights you learned from the web search to make the communication feel highly relevant and tailored.
        
        🔥 DRAFTING PROTOCOL:
        Write the copy for both Email and WhatsApp channels based on your research and the Schedule.
        - WhatsApp: Short, punchy, high urgency, uses emojis.
        - Email: Professional, highly detailed, highlights key schedule moments and research insights.
        
        Return ONLY valid JSON format exactly like this (escape internal double quotes with \\"):
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
            print(f"[*] CommsAgent: Browsing the web for {event_name} context before drafting...")
            
            # 🚀 We use the agent_executor so it can trigger the tools loop!
            res = await self.agent_executor.ainvoke({"messages": [("user", prompt)]})
            
            # The final output is the last message after the tools have finished running
            final_text = ""
            for msg in reversed(res["messages"]):
                content = getattr(msg, "content", "")
                if content and isinstance(content, str) and content.strip():
                    final_text = content.strip()
                    break
            
            if not final_text:
                raise ValueError("LLM returned an empty final response after tools.")

            # 🚀 2. BULLETPROOF JSON PARSING
            try:
                # Try the official Langchain parser first
                strategy = parse_json_markdown(final_text)
            except Exception:
                # If it fails, brutally extract the JSON block using Regex
                match = re.search(r'(\{.*\}|\[.*\])', final_text, re.DOTALL)
                if match:
                    strategy = json.loads(match.group(0))
                else:
                    raise ValueError(f"No JSON block found in response.")

            strategy["recipient"] = "All Participants"
            return strategy
            
        except Exception as e:
            print(f"[*] CommsAgent Error: {e}")
            return {
                "use_email": True, 
                "email_subject": f"Update regarding {event_name}", 
                "email_body": "Drafting failed. Please edit manually.",
                "use_whatsapp": False, 
                "whatsapp_body": "", 
                "status": "ERROR"
            }