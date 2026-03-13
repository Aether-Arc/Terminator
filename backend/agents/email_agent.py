import pandas as pd
import re
import io
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from config import OLLAMA_BASE_URL, OPENAI_API_KEY, LOCAL_MODEL
from tools.system_tools import swarm_tools

class EmailAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=LOCAL_MODEL,
            base_url=OLLAMA_BASE_URL,
            api_key=OPENAI_API_KEY,
            temperature=0.3
        )
        # 🚀 Bind the internet search tools to the email agent
        self.agent_executor = create_react_agent(self.llm, swarm_tools)

    def validate_email(self, email):
        return re.match(r"[^@]+@[^@]+\.[^@]+", str(email))

    async def draft_invites(self, event_data: dict, schedule: list, specifics: str):
        print(f"[*] EmailAgent: Researching & Drafting content for -> {specifics}")
        
        event_name = event_data.get("name", "our upcoming event")
        date = event_data.get("date", "a date to be announced")
        location = event_data.get("location", "TBD")
        
        prompt = f"""
        You are an expert corporate communications copywriter drafting an email for '{event_name}' taking place on {date} at {location}.
        
        SPECIFIC TASK: {specifics}
        
        MANDATORY TOOL USE:
        Use the 'web_search' tool to look up an interesting, recent statistic or exciting news fact related to the industry or theme of this event.
        
        Draft a highly engaging, professional email invite. Integrate the fact you just researched into the opening paragraph to hook the reader. 
        Keep the email concise, warm, and professional.
        """
        
        try:
            # 🚀 Agent will search the web, then write the email
            response = await self.agent_executor.ainvoke({"messages": [("user", prompt)]})
            return response["messages"][-1].content
        except Exception as e:
            print(f"[*] EmailAgent Error: {e}")
            return f"Subject: You're Invited to {event_name}!\n\nJoin us on {date} at {location} for an incredible experience. Regarding: {specifics}."

   

    def send_invites(self, csv_content=None, base_draft="You are invited to the event!"):
        print("[*] EmailAgent: Executing outreach protocol...")
        sent_logs = []
        
        # Check if CSV string was actually provided and isn't empty
        if csv_content and len(csv_content.strip()) > 0:
            try:
                # Parse the raw string as a CSV
                df = pd.read_csv(io.StringIO(csv_content))
                for _, row in df.iterrows():
                    # Handle different potential column names (case-insensitive)
                    cols = {c.lower(): c for c in df.columns}
                    email_col = cols.get('email', df.columns[0]) # fallback to first col
                    name_col = cols.get('name', None)
                    
                    email = row.get(email_col, '')
                    name = row.get(name_col, 'Participant') if name_col else 'Participant'
                    
                    if self.validate_email(email):
                        message = f"Hi {name},\n\n{base_draft}\n\nBest,\nSwarm AI"
                        sent_logs.append({"email": email, "status": "Drafted", "preview": message[:40] + "..."})
            except Exception as e:
                print(f"[*] EmailAgent Error parsing CSV string: {e}")
                sent_logs = [{"email": "error@system.com", "status": "Failed", "preview": "Failed to parse CSV"}]
        else:
            print("[*] EmailAgent: No CSV provided. Firing fallback mock.")
            sent_logs = [{"email": "hacker1@iit.edu", "status": "Mocked", "preview": base_draft[:40] + "..."}]

        return sent_logs