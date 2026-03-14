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
from agents.design_agent import DesignAgent
from agents.resource_agent import ResourceAgent
from config import get_resilient_llm

from orchestrator.workflow_graph import build_graph, Context
from tools.csv_parser import parse_messy_csv

from langchain_openai import ChatOpenAI
from config import OLLAMA_BASE_URL, OPENAI_API_KEY, CLOUD_MODEL
from langgraph.types import Command 

# 🚀 IMPORT YOUR REAL-WORLD SERVICES HERE
from services.whatsapp_service import send_whatsapp_blast

class EventOrchestrator:
    def __init__(self):
        self.planner = PlannerAgent()
        self.scheduler = SchedulerAgent()
        self.marketing = MarketingAgent()
        self.email = EmailAgent()
        self.budget = BudgetAgent()
        self.volunteer = VolunteerAgent()
        self.sponsor = SponsorAgent()
        self.updater_agent = UpdaterAgent()
        self.comms = CommsAgent() 
        self.design = DesignAgent()
        self.resource = ResourceAgent()
        
        self.graph = build_graph(
            self.planner, self.scheduler, self.marketing,
            self.comms, self.budget, self.volunteer, self.sponsor, 
            self.updater_agent, self.resource, self.design
        )
        
        self.user_context = Context(user_id="user_anmol") 
        self.llm = get_resilient_llm(temperature=0)

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
        print(f"[*] Orchestrator received event data: {event_data.get('name')}")
        raw_name = event_data.get("name", "Unnamed Event")
        short_hash = str(uuid.uuid4())[:4]
        self.thread_id = f"{raw_name} [{short_hash}]"
        await streamer.broadcast("Orchestrator", "Initializing Fast Zero-Shot Swarm Sequence...", "thinking")
        if not thread_id: thread_id = f"evt_{str(uuid.uuid4())[:8]}"
        
        self.thread_config = {"configurable": {"thread_id": self.thread_id}}
        raw_csv = event_data.get("csv_content", "")
        if raw_csv:
            await streamer.broadcast("Orchestrator", "Parsing messy CSV participant data...", "simulating")
            clean_participants = await parse_messy_csv(raw_csv)
            event_data["participants"] = clean_participants
        else:
            event_data["participants"] = []
            
        initial_state = {
            "event_data": event_data, "plan": {}, "schedule": [],
            "agent_outputs": {}, "audit_log": [], "completed_work": []
        }
        
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
            "email_outreach_logs": agent_outputs.get("comms", []), 
            "agent_outputs": agent_outputs
        }

    # ====================================================================
    # 🚀 NEW: THE UNIVERSAL GRAPH RESUMER 
    # (Replaces manual_override, approve_plan, conversational_micro_edit)
    # ====================================================================
    async def resume_workflow(self, thread_id, payload, streamer):
        """Passes ANY payload (approve, direct_edit, or prompt) back into the paused LangGraph node."""
        self.thread_config = {"configurable": {"thread_id": thread_id}}
        action = payload.get("action", "prompt")
        
        if action == "approve":
            await streamer.broadcast("Orchestrator", "Plan approved. Finalizing assets...", "success")
        elif action == "direct_edit":
            await streamer.broadcast("Orchestrator", "Injecting manual UI edits...", "warning")
        else:
            await streamer.broadcast("Orchestrator", "Activating Intelligence Swarm...", "thinking")

        # Stream the execution so the React UI Terminal gets live updates!
        async for chunk in self.graph.astream(Command(resume=payload), config=self.thread_config, stream_mode="updates", version="v2", context=self.user_context):
            if chunk["type"] == "updates":
                for node_name, state_update in chunk["data"].items():
                    await streamer.broadcast(node_name.capitalize(), "Applying changes...", "simulating")
                    
        final_state = self.graph.get_state(self.thread_config)
        await streamer.broadcast("Orchestrator", "Workflow paused/completed.", "idle")
        
        return {
            "schedule": final_state.values.get("schedule", []),
            "agent_outputs": final_state.values.get("agent_outputs", {}),
            "audit_log": final_state.values.get("audit_log", [])
        }

    async def route_user_intent(self, thread_id, user_prompt, streamer):
        """🚀 THE BRAIN: Categorizes if we are editing the plan OR sending live messages."""
        await streamer.broadcast("Orchestrator", "Analyzing command intent...", "thinking")
        
        routing_prompt = f"""
        Analyze this event management request: "{user_prompt}"
        Categorize it into exactly one of these:
        1. SEND_ACTION: User wants to physically send/dispatch emails, WhatsApps, or post content that was already drafted.
        2. CANCELLATION: User wants to cancel the event entirely.
        3. GRAPH_UPDATE: User wants to change times, edit text, add sessions, or modify the event plan.

        Return ONLY the category name.
        """
        
        response = await self.llm.ainvoke(routing_prompt)
        intent = response.content.strip().upper()

        if "SEND_ACTION" in intent:
            return await self.dispatch_outputs(thread_id, streamer)
        elif "CANCELLATION" in intent:
            await streamer.broadcast("Orchestrator", "Initiating Cancellation Protocol...", "error")
            cancelled_schedule = [{"time": "N/A", "session": "EVENT CANCELLED"}]
            return await self.resume_workflow(thread_id, {"action": "direct_edit", "schedule": cancelled_schedule}, streamer)
        else:
            # Let LangGraph's human_review node route it to the UpdaterAgent!
            return await self.resume_workflow(thread_id, {"action": "prompt", "message": user_prompt}, streamer)

    async def dispatch_outputs(self, thread_id, streamer):
        """Action: Physically sends the emails/whatsapps and updates state to SENT."""
        self.thread_config = {"configurable": {"thread_id": thread_id}}
        await streamer.broadcast("CommsAgent", "Executing Omnichannel Broadcast...", "simulating")
        
        state = self.graph.get_state(self.thread_config)
        agent_outputs = state.values.get("agent_outputs", {})
        comms_drafts = agent_outputs.get("comms", [])
        
        event_data = state.values.get("event_data", {})
        participants = event_data.get("participants", [])

        if not participants:
            await streamer.broadcast("Orchestrator", "WARNING: No participants found. Cannot dispatch.", "error")
            return {"error": "No participants found."}
        
        if not comms_drafts:
            return {"error": "No communications drafted yet."}
            
        dispatch_logs = []
            
        for draft in comms_drafts:
            payload = draft.get("output", {})
            if payload.get("status") == "SENT":
                continue
                
            payload["status"] = "SENT"
            
            if payload.get("use_whatsapp") and participants:
                await streamer.broadcast("CommsAgent", "Connecting to Twilio...", "simulating")
                try:
                    wa_logs = await send_whatsapp_blast(participants, payload.get("whatsapp_body", ""))
                    dispatch_logs.extend(wa_logs)
                    for log in wa_logs:
                        await streamer.broadcast("WhatsApp", log, "success" if "✅" in log else "error")
                except Exception as e:
                    print(f"Twilio Error: {e}")

        # Update state directly to save "SENT" statuses
        self.graph.update_state(self.thread_config, {"agent_outputs": agent_outputs})
        await streamer.broadcast("Orchestrator", "Omnichannel dispatched successfully.", "success")
        
        return {"status": "dispatched", "comms": comms_drafts, "logs": dispatch_logs}
        
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