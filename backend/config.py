import os
from dotenv import load_dotenv

# 🚀 1. CRITICAL FIX: Add this import!
from langchain_openai import ChatOpenAI 

load_dotenv()

# --- HYBRID SWARM CONFIGURATION ---
OLLAMA_BASE_URL = "http://localhost:11434/v1"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "ollama-local") 
# 🚀 HACKATHON TOGGLE: Set to True for deep evaluation, False for lightning-fast live demos
USE_CRITIC_AGENT = os.getenv("USE_CRITIC_AGENT", "False").lower() in ("true", "1", "t")

# 1. THE CLOUD HEAVYWEIGHT
CLOUD_MODEL = "llama3.1:8b-4096"

# 2. THE LOCAL WORKHORSE
LOCAL_MODEL = "llama3.1:8b-4096" 

def get_resilient_llm(temperature=0.5):
    """
    Creates a Hybrid LLM Router. 
    Tries NVIDIA NIM first. If it gets a 429 Too Many Requests, 
    it instantly falls back to the Local Ollama GPU.
    """
    
    # 1. Primary Engine: NVIDIA NIM (Fast Cloud)
    nvidia_llm = ChatOpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=os.getenv("NVIDIA_API_KEY", "your_nvidia_key"),
        model="meta/llama-3.3-70b-instruct", 
        temperature=temperature,
        max_retries=0, 
        timeout=15 
    )
    
    # 2. Fallback Engine: Local Ollama (Reliable Local)
    local_llm = ChatOpenAI(
        base_url=OLLAMA_BASE_URL,
        api_key="ollama", 
        model=LOCAL_MODEL, # 🚀 2. CRITICAL FIX: Use the Python variable directly!
        temperature=temperature,
        max_retries=1
    )
    
    # 3. The Magic Bind
    hybrid_llm = nvidia_llm.with_fallbacks([local_llm])
    
    return hybrid_llm

# --- DATABASES ---
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://postgres:postgres@localhost:5432/postgres")

# --- TERMINAL CONFIRMATION LOG ---
print("\n" + "="*60)
print(f"🚀 HYBRID AI ENGINE STATUS: ONLINE")
print(f"🧠 Brain/Logic Model: {CLOUD_MODEL} (Datacenter)")
print(f"⚡ Formatting Model:  {LOCAL_MODEL} (Local GPU)")
print("="*60 + "\n")