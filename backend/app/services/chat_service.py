import json
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from openai import AsyncOpenAI

from app.core.config import settings
from app.models.user import User, Message, Conversation
from app.schemas.chat import ChatRequest
from app.services.intent_router import IntentRouter, IntentType
from app.services.rag_service import RAGService
from app.services.web_search_service import WebSearchService
from app.services.context_assembler import ContextAssembler
from app.services.profile_agent import ProfileExtractionAgent

class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.intent_router = IntentRouter()
        self.rag_service = RAGService()
        self.web_search_service = WebSearchService()
        self.context_assembler = ContextAssembler()
        self.profile_agent = ProfileExtractionAgent(db)
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

    async def chat(self, user: User, request: ChatRequest) -> AsyncGenerator[str, None]:
        # 1. Get or Create Conversation
        conversation_id = request.conversation_id
        if not conversation_id:
            # Create new conversation
            new_conv = Conversation(user_id=user.id, title=request.message[:20])
            self.db.add(new_conv)
            await self.db.commit()
            await self.db.refresh(new_conv)
            conversation_id = new_conv.id
        else:
            # Verify ownership
            result = await self.db.execute(select(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == user.id))
            if not result.scalar_one_or_none():
                 yield self._sse_error("Conversation not found")
                 return

        # 2. Intent Classification
        intent_result = await self.intent_router.classify(request.message)
        
        # 3. Retrieval (RAG / Web)
        rag_products = []
        web_results = []
        sources = []

        if intent_result.intent == IntentType.PRODUCT_KNOWLEDGE:
            rag_result = await self.rag_service.retrieve(request.message)
            rag_products = rag_result.products
            
            if rag_result.below_threshold:
                # Fallback to web search if no good product match
                web_results = await self.web_search_service.search(request.message)
                sources.extend([{"type": "web", "title": r.title, "url": r.url} for r in web_results])
            else:
                 sources.extend([{"type": "product", "title": p.product_name, "url": None} for p in rag_products])
                 
        elif intent_result.intent == IntentType.EXTERNAL_KNOWLEDGE:
            web_results = await self.web_search_service.search(request.message)
            sources.extend([{"type": "web", "title": r.title, "url": r.url} for r in web_results])

        # 4. Load History
        history_result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        chat_history = history_result.scalars().all()

        # 5. Assemble Prompt
        messages = self.context_assembler.assemble(
            current_query=request.message,
            rag_products=rag_products,
            web_results=web_results,
            user_profile=user.profile,
            chat_history=list(chat_history)
        )

        # 6. Stream Response
        full_response = ""
        
        if self.openai_client:
            try:
                stream = await self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    stream=True,
                    temperature=0.7
                )
                
                async for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        full_response += content
                        yield self._sse_data({"content": content})
                        
                # Send sources at the end
                if sources:
                    yield self._sse_data({"sources": sources})
                    
            except Exception as e:
                yield self._sse_error(f"LLM Error: {str(e)}")
                return
        else:
            # Mock response if no API key
            mock_resp = "I'm sorry, I cannot process your request because the OpenAI API key is missing."
            full_response = mock_resp
            yield self._sse_data({"content": mock_resp})

        # 7. Save Messages to DB
        # User Message
        user_msg = Message(
            conversation_id=conversation_id,
            user_id=user.id,
            role="user",
            content=request.message
        )
        self.db.add(user_msg)
        
        # Assistant Message
        assistant_msg = Message(
            conversation_id=conversation_id,
            user_id=user.id,
            role="assistant",
            content=full_response,
            sources=sources
        )
        self.db.add(assistant_msg)
        
        await self.db.commit()
        
        # Yield conversation ID to client if it was new
        yield self._sse_data({"conversation_id": conversation_id, "done": True})

        # 8. Async Profile Extraction (Trigger every 5 messages or simplified trigger)
        # For MVP, we can just trigger it. In production, use background tasks (FastAPI BackgroundTasks)
        # to avoid blocking the response if not streaming, but here we are streaming.
        # However, since this is a generator, we can't easily run background task after yield.
        # We should accept BackgroundTasks in the API endpoint.
        # For now, let's just do it here or better, inject it in the endpoint.
        pass

    def _sse_data(self, data: dict) -> str:
        return f"data: {json.dumps(data)}\n\n"

    def _sse_error(self, message: str) -> str:
        return f"data: {json.dumps({'error': message})}\n\n"
