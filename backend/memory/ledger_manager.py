import json
import os
import asyncio

class LedgerManager:
    def __init__(self, thread_id: str):
        self.thread_id = thread_id
        self.filepath = f"memory/ledgers/{thread_id}_master.json"
        
        # This Lock is the magic that prevents parallel agents from crashing the file
        self.lock = asyncio.Lock() 
        
        # Ensure the directory exists
        os.makedirs("memory/ledgers", exist_ok=True)
        
        # Initialize an empty, structured ledger if this is a brand new event
        if not os.path.exists(self.filepath):
            self._initialize_ledger()

    def _initialize_ledger(self):
        """Creates the foundational structure of the Master Event Ledger."""
        base_ledger = {
            "event_metadata": {},
            "participants": [],        # Replaces the flat CSV
            "schedule": [],            # Replaces the isolated GraphState schedule
            "budget": {
                "total_estimated": 0, 
                "breakdown": {}
            },
            "volunteers": [],
            "marketing_assets": {},
            "sponsors": [],
            "crisis_logs": []
        }
        with open(self.filepath, "w") as f:
            json.dump(base_ledger, f, indent=4)

    async def read_ledger(self) -> dict:
        """Agents call this to 'look at the blackboard' and see the current state of the event."""
        async with self.lock:
            if not os.path.exists(self.filepath):
                self._initialize_ledger()
            with open(self.filepath, "r") as f:
                return json.load(f)

    async def update_ledger(self, section: str, data: any):
        """Agents call this to 'write on the blackboard' under their specific section."""
        async with self.lock:
            # 1. Read the current state
            with open(self.filepath, "r") as f:
                ledger = json.load(f)
            
            # 2. Update ONLY the specific section (e.g., "budget" or "participants")
            ledger[section] = data
            
            # 3. Save it back to disk instantly so the UI can fetch it
            with open(self.filepath, "w") as f:
                json.dump(ledger, f, indent=4)
                
    async def get_participants_df(self):
        """Helper method: returns participants as a list of dictionaries (easy ML parsing)"""
        ledger = await self.read_ledger()
        return ledger.get("participants", [])