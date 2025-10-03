import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from models import Session as DBSession, Message
from datetime import datetime
from typing import Optional, Dict
from sqlalchemy import select


# ---- Helper functions ----
async def create_or_get_session(db: AsyncSession, session_id: Optional[str], user_id: Optional[str]):
    if session_id:
        result = await db.execute(
            DBSession.__table__.select().where(DBSession.session_id == session_id)
        )
        row = result.first()
        if row:
            session_row = row[0]
            session_row.last_active_at = datetime.utcnow()
            await db.commit()
            return session_row
    # create new session
    new_session_id = str(uuid.uuid4())
    session_row = DBSession(session_id=new_session_id, user_id=user_id)
    db.add(session_row)
    await db.commit()
    await db.refresh(session_row)
    return session_row

async def save_message(db: AsyncSession, session_row: DBSession, role: str, text: str, metadata: Optional[Dict]=None):
    m = Message(session_id=session_row.id, role=role, text=text, metadata=metadata or {})
    db.add(m)
    await db.commit()
    await db.refresh(m)
    return m

async def get_recent_messages(db: AsyncSession, session_row: DBSession, limit=10):
    q = (
        select(Message)
        .where(Message.session_id == session_row.id)
        .order_by(Message.id.desc())
        .limit(limit)
    )
    res = await db.execute(q)
    rows = res.scalars().all()  # ✅ get list of Message objects

    # rows are newest->oldest; reverse for chronological order
    msgs = [
        {
            "role": m.role,
            "text": m.text,
            "timestamp": m.timestamp.isoformat(),
        }
        for m in reversed(rows)
    ]
    return msgs
