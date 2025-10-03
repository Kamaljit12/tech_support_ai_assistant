import requests
from langchain_groq import ChatGroq
from langchain.agents import initialize_agent, Tool
from config import Config

# ---- STT Adapter ----
class STTAdapter:
    async def transcribe_bytes(self, audio_bytes: bytes) -> str:
        """Dummy STT (replace with Whisper, Deepgram, etc.)"""
        return f"[transcribed audio length={len(audio_bytes)}]"


# ---- TTS Adapter ----
class TTSAdapter:
    async def synthesize(self, text: str) -> bytes:
        """Dummy TTS (replace with ElevenLabs, Azure, etc.)"""
        return text.encode("utf-8")


# ---- Example Tools ----
def calculator(expression: str) -> str:
    """Evaluate a math expression safely."""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Error: {e}"


def web_search(query: str) -> str:
    """Naive web search using DuckDuckGo."""
    try:
        r = requests.get(f"https://duckduckgo.com/html/?q={query}", timeout=5)
        return f"Search returned {len(r.text)} characters of HTML"
    except Exception as e:
        return f"Error searching web: {e}"


tools = [
    Tool(
        name="Calculator",
        func=calculator,
        description="Useful for solving math expressions."
    ),
    Tool(
        name="Web Search",
        func=web_search,
        description="Useful for searching the web."
    ),
]


# ---- LLM Adapter (Groq) ----
class LLMAdapter:
    def __init__(self, model_name: str = Config.LLM_MODEL, temperature: float = Config.TEMPERATURE):
        """
        Uses Groq LLM via LangChain.
        Requires GROQ_API_KEY set in environment.
        """
        self.llm = ChatGroq(api_key=Config.GROQ_API_KEY , model=model_name, temperature=temperature)

        # Initialize agent with tools
        self.agent = initialize_agent(
            tools,
            self.llm,
            agent="zero-shot-react-description",
            verbose=True
        )

    async def generate(self, prompt: str, tools=None) -> str:
        """Call Groq LLM + tools through LangChain agent."""
        try:
            result = await self.agent.ainvoke(prompt)
            return result["output"]
        except Exception as e:
            return f"[LLM error: {e}]"
