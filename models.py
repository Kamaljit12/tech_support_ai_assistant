# models.py
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Text, JSON)
from sqlalchemy.orm import declarative_base, relationship
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

Base = declarative_base()

class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(128), unique=True, index=True, nullable=False)
    user_id = Column(String(128), nullable=True)  # if you have auth
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active_at = Column(DateTime, default=datetime.utcnow)
    extra = Column(JSON, nullable=True)  # 🔹 renamed from metadata

    messages = relationship("Message", back_populates="session")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), index=True)
    role = Column(String(16), nullable=False)  # user | assistant | system | tool
    text = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    audio_path = Column(String(512), nullable=True)
    extra = Column(JSON, nullable=True)  # 🔹 renamed from metadata

    session = relationship("Session", back_populates="messages")

class ConversationSummary(Base):
    __tablename__ = "conversation_summaries"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), index=True)
    summary_text = Column(Text, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow)

class ToolLog(Base):
    __tablename__ = "tool_logs"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), index=True)
    tool_name = Column(String(128))
    input = Column(Text)
    output = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)



# ---- Pydantic Chat models----
class ChatRequest(BaseModel):
    session_id: Optional[str]
    text: str
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    session_id: str
    assistant_text: str
    tts_audio_url: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
