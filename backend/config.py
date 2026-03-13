import os
from dotenv import load_dotenv

load_dotenv()

# --- HYBRID SWARM CONFIGURATION ---
OLLAMA_BASE_URL = "http://localhost:11434/v1"
OPENAI_API_KEY = "ollama-local" # Dummy key for Langchain's OpenAI wrapper

# 1. THE CLOUD HEAVYWEIGHT (0GB VRAM - Runs on Ollama Datacenter)
# Use this strictly for complex reasoning, tool-calling, and conflict resolution
CLOUD_MODEL = "llama3.1:8b-4096"

# 2. THE LOCAL WORKHORSE (Fits in 6GB VRAM - Runs on your RTX 4050)
# Use this for basic JSON formatting, email drafting, and social media copy
LOCAL_MODEL = "llama3.1:8b-4096" 

# --- DATABASES ---
REDIS_URL = os.getenv("REDIS_URL", "redis://default:ATkIAAIncDExMzZkNjkxYzE5ZmU0ZTFkYjM2YzRhODg5Yjg1ZjViYXAxMTQ2MDA@knowing-ant-14600.upstash.io:6379")
POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://postgres:Doraemon1Pokemo@db.chmdfgdyqnkjjfitibki.supabase.co:5432/postgres")

# --- TERMINAL CONFIRMATION LOG ---
print("\n" + "="*60)
print(f"🚀 HYBRID AI ENGINE STATUS: ONLINE")
print(f"🧠 Brain/Logic Model: {CLOUD_MODEL} (Datacenter)")
print(f"⚡ Formatting Model:  {LOCAL_MODEL} (Local GPU)")
print("="*60 + "\n")