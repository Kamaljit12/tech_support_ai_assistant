import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    # ---- CONFIG ----
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # placeholder
    STT_PROVIDER = os.getenv("STT_PROVIDER", "whisper")
    TTS_PROVIDER = os.getenv("TTS_PROVIDER", "elevenlabs")
    MAX_CONTEXT_MESSAGES = 10
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    LLM_MODEL = "llama-3.1-8b-instant"
    TEMPERATURE = 0.5