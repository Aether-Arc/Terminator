import asyncio
import uuid
import sqlite3
import os
import json
import re

from agents.planner_agent import PlannerAgent
from agents.scheduler_agent import SchedulerAgent
from agents.marketing_agent import MarketingAgent
from agents.updater_agent import UpdaterAgent
from agents.email_agent import EmailAgent
from agents.budget_agent import BudgetAgent
from agents.volunteer_agent import VolunteerAgent
from agents.sponsor_agent import SponsorAgent
from agents.comms_agent import CommsAgent
from orchestrator.workflow_graph import build_graph, Context
from tools.csv_parser import parse_messy_csv
from agents.design_agent import DesignAgent

from langchain_openai import ChatOpenAI
from config import OLLAMA_BASE_URL, OPENAI_API_KEY, CLOUD_MODEL
from langgraph.types import Command # 🚀 Required to resume from interrupts

# 🚀 IMPORT YOUR REAL-WORLD SERVICES HERE
from services.whatsapp_service import send_whatsapp_blast
# from services.email_service import send_email_blast  <-- Import your email script when ready!

class EventOrchestrator:
    def __init__(self):
        # 1. Initialize Clean Agents
        self.planner = PlannerAgent()
        self.scheduler = SchedulerAgent()
        self.marketing = MarketingAgent()
        self.email = EmailAgent()
        self.budget = BudgetAgent()
        self.volunteer = VolunteerAgent()
        self.sponsor = SponsorAgent()
        self.updater_agent = UpdaterAgent()
        self.comms = CommsAgent() # 🚀 Omnichannel Comms Agent
        self.design = DesignAgent()
        
        self.graph = build_graph(
            self.planner, self.scheduler, self.marketing,
            self.comms, self.budget, self.volunteer, self.sponsor, self.updater_agent,  self.design
        )
        
        self.user_context = Context(user_id="user_anmol") 
        self.llm = ChatOpenAI(model=CLOUD_MODEL, base_url=OLLAMA_BASE_URL, api_key=OPENAI_API_KEY, temperature=0)

    def get_thread_history(self):
        db_path = os.path.join(os.getcwd(), "memory", "swarm_threads.sqlite")
        if not os.path.exists(db_path): return []
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT thread_id FROM checkpoints")
                rows = cursor.fetchall()
                return [row[0] for row in rows]
        except Exception as e:
            print(f"DB Read Error: {e}")
            return []

    async def plan_event(self, event_data, streamer, thread_id=None):
        await streamer.broadcast("Orchestrator", "Initializing Fast Zero-Shot Swarm Sequence...", "thinking")
        if not thread_id: thread_id = f"evt_{str(uuid.uuid4())[:8]}"
        
        self.thread_config = {"configurable": {"thread_id": thread_id}}
        raw_csv = event_data.get("csv_content", "")
        if raw_csv:
            await streamer.broadcast("Orchestrator", "Parsing messy CSV participant data...", "simulating")
            clean_participants = await parse_messy_csv(raw_csv)
            # Inject it into event_data so it lives forever in LangGraph SQLite!
            event_data["participants"] = clean_participants
        else:
            event_data["participants"] = []
        initial_state = {
            "event_data": event_data, "plan": {}, "schedule": [],
            "agent_outputs": {}, "audit_log": [], "completed_work": []
        }
        
        # Runs until it hits the interrupt() inside the human_review node
        async for chunk in self.graph.astream(initial_state, config=self.thread_config, stream_mode="updates", version="v2", context=self.user_context):
            if chunk["type"] == "updates":
                for node_name, state_update in chunk["data"].items():
                    await streamer.broadcast(node_name.capitalize(), "Autonomously generating plan...", "simulating")
        
        final_state = self.graph.get_state(self.thread_config)
        agent_outputs = final_state.values.get("agent_outputs", {})
        
        return {
            "thread_id": thread_id,
            "workflow_executed": True,
            "selected_plan": final_state.values.get("plan"),
            "schedule": final_state.values.get("schedule"),
            "marketing": agent_outputs.get("marketing", []),
            "email_outreach_logs": agent_outputs.get("comms", []), # Pointing to comms now
            "agent_outputs": agent_outputs
        }

    async def approve_plan(self, event_data, streamer):
        """Passes 'approve' to the paused interrupt(), launching the universal parallel workers."""
        await streamer.broadcast("Orchestrator", "Plan approved. Engaging Universal Orchestrator-Worker Subgraph...", "simulating")
        
        # 🚀 Resume the interrupted graph with the explicit "approve" command!
        async for chunk in self.graph.astream(Command(resume="approve"), config=self.thread_config, stream_mode="updates", version="v2", context=self.user_context):
            if chunk["type"] == "updates":
                for node_name, state_update in chunk["data"].items():
                    await streamer.broadcast(node_name.capitalize(), "Autonomously executing parallel task...", "simulating")

        final_state = self.graph.get_state(self.thread_config)
        await streamer.broadcast("Orchestrator", "All operational phases autonomously completed.", "idle")
        
        agent_outputs = final_state.values.get("agent_outputs", {})
        
        return {
            "status": "approved_and_completed",
            "marketing": agent_outputs.get("marketing", []),
            "email_outreach_logs": agent_outputs.get("comms", []),
            "operations": agent_outputs.get("operations", [])
        }

    async def fork_and_update(self, thread_id, new_prompt, streamer):
        """Passes the user's feedback text to the paused interrupt() to trigger a replan."""
        self.thread_config = {"configurable": {"thread_id": thread_id}}
        await streamer.broadcast("Orchestrator", f"Sending constraints to Planner for {thread_id}...", "warning")
        
        async for chunk in self.graph.astream(Command(resume=new_prompt), config=self.thread_config, stream_mode="updates", version="v2", context=self.user_context):
            if chunk["type"] == "updates":
                for node_name, state_update in chunk["data"].items():
                    await streamer.broadcast(node_name.capitalize(), "Applying feedback & replanning...", "simulating")
                    
        final_state = self.graph.get_state(self.thread_config)
        return {
            "status": "forked_and_replanned",
            "schedule": final_state.values.get("schedule", [])
        }   

    async def route_user_intent(self, thread_id, user_prompt, streamer):
        """
        🚀 THE BRAIN: Categorizes the prompt and directs it to the correct surgical action.
        """
        await streamer.broadcast("Orchestrator", "Analyzing command intent...", "thinking")
        
        routing_prompt = f"""
        Analyze this event management request: "{user_prompt}"
        Categorize it into exactly one of these:
        1. SEND_ACTION: User wants to physically send/dispatch emails or post content that was already drafted.
        2. MICRO_EDIT: User wants to change times, postpone, delay, or fix small text details without changing the event structure.
        3. CANCELLATION: User wants to cancel the event entirely.
        4. FULL_REPLAN: User wants to change the theme, add new sessions, or fundamentally alter the event flow.

        Return ONLY the category name.
        """
        
        response = await self.llm.ainvoke(routing_prompt)
        intent = response.content.strip().upper()

        if "SEND_ACTION" in intent:
            return await self.dispatch_outputs(thread_id, streamer)
        elif "MICRO_EDIT" in intent:
            return await self.conversational_micro_edit(thread_id, user_prompt, streamer)
        elif "CANCELLATION" in intent:
            return await self.handle_cancellation(thread_id, streamer)
        else:
            return await self.fork_and_update(thread_id, user_prompt, streamer)

    async def dispatch_outputs(self, thread_id, streamer):
        """Action: Physically sends the emails/whatsapps and updates state to SENT."""
        self.thread_config = {"configurable": {"thread_id": thread_id}}
        await streamer.broadcast("CommsAgent", "Executing Omnichannel Broadcast...", "simulating")
        
        state = self.graph.get_state(self.thread_config)
        agent_outputs = state.values.get("agent_outputs", {})
        comms_drafts = agent_outputs.get("comms", [])
        
        # We need the participant list to send the actual messages!
        event_data = state.values.get("event_data", {})
        participants = event_data.get("participants", []) # Or parse it from event_data.get("csv_content")

        if not participants:
            await streamer.broadcast("Orchestrator", "WARNING: No participants found. Cannot dispatch.", "error")
            return {"error": "No participants found."}
        
        if not comms_drafts:
            return {"error": "No communications drafted yet."}
            
        dispatch_logs = []
            
        # Update status to SENT & TRIGGER EXTERNAL APIs
        for draft in comms_drafts:
            payload = draft.get("output", {})
            
            # Skip if already sent to avoid double-texting
            if payload.get("status") == "SENT":
                continue
                
            payload["status"] = "SENT"
            
            # 🚀 EXECUTE WHATSAPP ASYNC
            if payload.get("use_whatsapp") and participants:
                await streamer.broadcast("CommsAgent", "Connecting to Twilio...", "simulating")
                try:
                    wa_logs = await send_whatsapp_blast(participants, payload.get("whatsapp_body", ""))
                    dispatch_logs.extend(wa_logs)
                    for log in wa_logs:
                        await streamer.broadcast("WhatsApp", log, "success" if "✅" in log else "error")
                except Exception as e:
                    print(f"Twilio Error: {e}")

            # 🚀 EXECUTE EMAIL ASYNC (Add when ready)
            if payload.get("use_email") and participants:
                await streamer.broadcast("CommsAgent", "Connecting to SMTP...", "simulating")
                # email_logs = await send_email_blast(participants, payload.get("email_subject"), payload.get("email_body"))
                # dispatch_logs.extend(email_logs)

        # Update the LangGraph state directly (Durable Execution)
        self.graph.update_state(self.thread_config, {"agent_outputs": agent_outputs})
        await streamer.broadcast("Orchestrator", "Omnichannel dispatched successfully.", "success")
        
        return {"status": "dispatched", "comms": comms_drafts, "logs": dispatch_logs}

    async def handle_cancellation(self, thread_id, streamer):
        """Action: Wipes schedule and triggers the execution phase to draft cancellation copy."""
        self.thread_config = {"configurable": {"thread_id": thread_id}}
        await streamer.broadcast("Orchestrator", "Initiating Cancellation Protocol...", "warning")
        
        cancelled_schedule = [{"time": "N/A", "session": "EVENT CANCELLED"}]
        self.graph.update_state(self.thread_config, {"schedule": cancelled_schedule})
        
        return await self.approve_plan(None, streamer)

    async def conversational_micro_edit(self, thread_id, user_prompt, streamer):
        """Fast JSON-manipulation for delays without a full replan."""
        self.thread_config = {"configurable": {"thread_id": thread_id}}
        await streamer.broadcast("Orchestrator", f"Processing targeted schedule adjustment...", "thinking")
        
        current_state = self.graph.get_state(self.thread_config)
        current_schedule = current_state.values.get("schedule", [])
        
        if not current_schedule: return {"error": "No schedule exists yet to edit."}

        editor_prompt = f"""
        You are a precise JSON text editor.
        CURRENT SCHEDULE JSON: {json.dumps(current_schedule)}
        USER REQUEST: "{user_prompt}"
        INSTRUCTIONS: Apply the user's requested time/day shifts to the schedule. DO NOT change session names.
        Respond ONLY with the updated raw JSON array.
        """
        
        await streamer.broadcast("Copilot", "Calculating new timeline physics...", "simulating")
        response = await self.llm.ainvoke(editor_prompt)
        
        match = re.search(r'\[.*\]', response.content, re.DOTALL)
        if not match: return {"error": "Failed to parse AI schedule adjustment."}
            
        new_schedule = json.loads(match.group(0))
        
        self.graph.update_state(self.thread_config, {"schedule": new_schedule})
        await streamer.broadcast("Orchestrator", "Schedule shifted. Click 'Approve' to lock it in.", "success")
        
        return {
            "status": "micro_edit_completed_awaiting_approval",
            "schedule": new_schedule
        }

    async def manual_override(self, override_data, streamer):
        """Allows direct JSON edits from the UI table."""
        action_type = override_data.get("override_type") 
        if action_type == "edit_schedule":
            await streamer.broadcast("Orchestrator", "Manual schedule override initiated.", "warning")
            new_schedule = override_data.get("new_schedule", [])
            
            self.graph.update_state(self.thread_config, {"schedule": new_schedule})
            await streamer.broadcast("Orchestrator", "Schedule updated in memory. Awaiting approval.", "success")
            
            return {"status": "Schedule manually updated.", "new_schedule": new_schedule}
        return {"error": "Unknown override type."}
    
    async def resume_event(self, streamer):
        await streamer.broadcast("Orchestrator", "CRASH RECOVERY INITIATED...", "warning")
        self.thread_config = {"configurable": {"thread_id": "event_thread_1"}}
        
        saved_state = self.graph.get_state(self.thread_config)
        next_agent = saved_state.next 
        if not next_agent:
            await streamer.broadcast("Orchestrator", "Thread already completed.", "idle")
            return {"status": "completed"}

        await streamer.broadcast("Orchestrator", f"Resuming execution at: {next_agent[0].capitalize()}", "success")
        
        async for chunk in self.graph.astream(None, config=self.thread_config, stream_mode="updates", version="v2", context=self.user_context):
            if chunk["type"] == "updates":
                for node_name, state_update in chunk["data"].items():
                    await streamer.broadcast(node_name.capitalize(), "Autonomously executing task...", "simulating")

        final_state = self.graph.get_state(self.thread_config)
        agent_outputs = final_state.values.get("agent_outputs", {})
        return {
            "status": "recovered",
            "schedule": final_state.values.get("schedule", []),
            "marketing": agent_outputs.get("marketing", []),
            "operations": agent_outputs.get("operations", [])
        }

    def get_event_details(self, thread_id):
        self.thread_config = {"configurable": {"thread_id": thread_id}}
        state = self.graph.get_state(self.thread_config)
        if not state or not hasattr(state, 'values'): return {"error": "Thread not found or event not finished."}
        agent_outputs = state.values.get("agent_outputs", {})
        return {
            "thread_id": thread_id,
            "schedule": state.values.get("schedule", []),
            "marketing_copy": agent_outputs.get("marketing", []),
            "email_logs": agent_outputs.get("comms", []),
            "agent_outputs": agent_outputs
        }