from memory.redis_memory import store_state, get_state
from memory.vector_store import store_memory, search_memory

class EventMemory:
    def save_active_schedule(self, schedule_json):
        # Short term memory for the current event
        store_state("current_schedule", str(schedule_json))
        
    def get_active_schedule(self):
        return get_state("current_schedule")
        
    def learn_from_event(self, post_mortem_text):
        # Long term memory for future hackathons to learn from
        store_memory(post_mortem_text)
        
    def recall_past_lessons(self, query):
        return search_memory(query)