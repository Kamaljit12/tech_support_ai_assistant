import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models import ConversationSummary
from datetime import datetime
from db import get_db, init_db, AsyncSessionLocal
from models import ChatRequest, ChatResponse
from memory import get_recent_messages, save_message
from plugins import STTAdapter, TTSAdapter, LLMAdapter
from helpers import create_or_get_session, save_message
import os


# ---- FastAPI ----
app = FastAPI(on_startup=[init_db])


# instantiate adapters (swap with real implementations)
stt = STTAdapter()
tts = TTSAdapter()
llm = LLMAdapter()



@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    # 1. session retrieval / creation
    session_row = await create_or_get_session(db, req.session_id, req.user_id)

    # 2. save user message
    await save_message(db, session_row, "user", req.text, metadata=req.metadata)

    # 3. gather context + summary
    recent_messages = await get_recent_messages(db, session_row)
    # build prompt (include summary if exists)
    # Note: you should incorporate conversation summary + recent messages for long contexts
    prompt_parts = []
    # fetch summary
    s = await db.execute(ConversationSummary.__table__.select().where(ConversationSummary.session_id == session_row.id))
    summary_row = s.first()
    if summary_row:
        prompt_parts.append(f"Conversation summary: {summary_row[0].summary_text}")
    for m in recent_messages:
        prompt_parts.append(f"{m['role']}: {m['text']}")
    prompt_parts.append("assistant:")

    prompt = "\n".join(prompt_parts)

    # 4. call LLM (sync/async adapter)
    assistant_text = await llm.generate(prompt)

    # 5. save assistant message
    await save_message(db, session_row, "assistant", assistant_text)

    # 6. run TTS asynchronously to generate audio bytes and store file or return stream
    audio_bytes = await tts.synthesize(assistant_text)
    # Save audio to disk and produce URL (in prod use S3 and presigned URL)
    audio_dir = "./audio_out"
    os.makedirs(audio_dir, exist_ok=True)
    audio_path = f"{audio_dir}/{session_row.session_id}_{int(datetime.utcnow().timestamp())}.wav"
    with open(audio_path, "wb") as f:
        f.write(audio_bytes)

    # store audio path in message metadata (optional)
    # This example does not update message row; for production update the assistant message with audio_path.

    return ChatResponse(
        session_id=session_row.session_id,
        assistant_text=assistant_text,
        tts_audio_url=audio_path
    )

# ---- WebSocket for streaming audio -> STT -> assistant replies ----
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    # We'll accept binary frames with audio bytes, or JSON control frames
    try:
        # Create or get session (without using DB dependency in WS)
        async with AsyncSessionLocal() as db:
            session_row = await create_or_get_session(db, session_id, None)
            while True:
                data = await websocket.receive()
                # If the client sends an audio chunk in bytes
                if "bytes" in data:
                    audio_bytes = data["bytes"]
                    # Call STT adapter
                    transcript = await stt.transcribe_bytes(audio_bytes)
                    # Save partial user message? Optionally store streaming partials
                    await save_message(db, session_row, "user", transcript, metadata={"partial": True})
                    # send partial transcript back
                    await websocket.send_json({"type": "transcript.partial", "text": transcript})
                elif "text" in data:
                    # control or final text (e.g., {"type": "finalize"} or {"type":"user_text","text":"..."}
                    msg = data["text"]
                    # expect JSON string
                    import json
                    payload = json.loads(msg)
                    if payload.get("type") == "user_text":
                        user_text = payload.get("text", "")
                        # save final user message
                        await save_message(db, session_row, "user", user_text)
                        # Build prompt and call LLM
                        recent_messages = await get_recent_messages(db, session_row)
                        prompt = "\n".join([f"{m['role']}: {m['text']}" for m in recent_messages] + ["assistant:"])
                        assistant_text = await llm.generate(prompt)
                        await save_message(db, session_row, "assistant", assistant_text)
                        # TTS
                        audio_bytes = await tts.synthesize(assistant_text)
                        # send assistant text and audio bytes (base64)
                        import base64
                        b64_audio = base64.b64encode(audio_bytes).decode("ascii")
                        await websocket.send_json({
                            "type": "assistant_response",
                            "text": assistant_text,
                            "audio_b64": b64_audio
                        })
                    elif payload.get("type") == "close":
                        break
                else:
                    await asyncio.sleep(0.01)
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        await websocket.close(code=1011)
        raise

# Basic health check
@app.get("/health")
async def health():
    return {"status": "ok"}