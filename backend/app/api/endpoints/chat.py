from typing import Annotated
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.chat import ChatRequest
from app.services.chat_service import ChatService

router = APIRouter()

@router.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    chat_service = ChatService(db)
    
    return StreamingResponse(
        chat_service.chat(current_user, request),
        media_type="text/event-stream"
    )
