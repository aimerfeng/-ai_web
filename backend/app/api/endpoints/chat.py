from typing import Annotated
from fastapi import APIRouter, Depends, Request, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User, Message
from app.schemas.chat import ChatRequest
from app.services.chat_service import ChatService
from app.services.profile_agent import ProfileExtractionAgent

router = APIRouter()

@router.post("/chat")
async def chat(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    chat_service = ChatService(db)
    
    # Define background task for profile extraction
    async def run_profile_extraction(user_id: str, conversation_id: str):
        # We need a new DB session for background task
        async for session in get_db():
            agent = ProfileExtractionAgent(session)
            # Fetch recent history
            result = await session.execute(
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.created_at.desc())
                .limit(20)
            )
            history = result.scalars().all()
            # Reverse to chronological order
            history = list(reversed(history))
            
            await agent.extract_and_update(user_id, history)
            break # Close session

    # Trigger every 5 messages? For now, trigger on every chat to ensure it works for demo
    # In real app, check message count % 5 == 0
    if request.conversation_id:
        background_tasks.add_task(run_profile_extraction, current_user.id, request.conversation_id)

    return StreamingResponse(
        chat_service.chat(current_user, request),
        media_type="text/event-stream"
    )
