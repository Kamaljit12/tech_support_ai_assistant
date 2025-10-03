from langchain_core.memory import BaseMemory
from helpers import get_recent_messages, save_message


class SQLConversationMemory(BaseMemory):
    def __init__(self, db_session, session_row, k=10):
        self.db = db_session
        self.session_row = session_row
        self.k = k

    async def load_memory_variables(self, inputs):
        msgs = await get_recent_messages(self.db, self.session_row, limit=self.k)
        return {"history": "\n".join([f"{m['role']}: {m['text']}" for m in msgs])}

    async def save_context(self, inputs, outputs):
        # inputs: {"input": "user text"}, outputs: {"output": "assistant text"}
        await save_message(self.db, self.session_row, "user", inputs.get("input"))
        await save_message(self.db, self.session_row, "assistant", outputs.get("output"))
