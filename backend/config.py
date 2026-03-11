import os
from dotenv import load_dotenv

load_dotenv()

# --- NEW OLLAMA CONFIGURATION ---
# We no longer need the real OpenAI API key. We use a dummy key.
OPENAI_API_KEY = "ollama-local" 
OLLAMA_BASE_URL = "http://localhost:11434/v1"
AI_MODEL = "gemma2-fast"

REDIS_URL = os.getenv("REDIS_URL", "redis://default:ATkIAAIncDExMzZkNjkxYzE5ZmU0ZTFkYjM2YzRhODg5Yjg1ZjViYXAxMTQ2MDA@knowing-ant-14600.upstash.io:6379")

POSTGRES_URL = os.getenv(
    "POSTGRES_URL",
    "postgresql://postgres:Doraemon1Pokemo@db.chmdfgdyqnkjjfitibki.supabase.co:5432/postgres"
)

# --- TERMINAL CONFIRMATION LOG ---
print("\n" + "="*60)
print(f"🚀 AI ENGINE STATUS: ONLINE")
print(f"🧠 Active Model: {AI_MODEL} (Running Locally via Ollama)")
print(f"🔗 Server URL:   {OLLAMA_BASE_URL}")
print("="*60 + "\n")