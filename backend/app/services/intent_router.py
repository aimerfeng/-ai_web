from enum import Enum
from pydantic import BaseModel
from openai import AsyncOpenAI
from app.core.config import settings

class IntentType(str, Enum):
    PRODUCT_KNOWLEDGE = "product_knowledge"
    GENERAL_CHAT = "general_chat"
    EXTERNAL_KNOWLEDGE = "external_knowledge"

class IntentResult(BaseModel):
    intent: IntentType
    confidence: float
    used_llm_fallback: bool

class IntentRouter:
    CONFIDENCE_THRESHOLD = 0.6
    
    # Keyword patterns
    PRODUCT_KEYWORDS = ["推荐", "成分", "护肤品", "面霜", "精华", "乳液", "防晒", "美白", "抗老", "祛痘", "洗面奶", "水杨酸", "A醇", "玻尿酸"]
    EXTERNAL_KEYWORDS = ["最新", "2025", "新品", "趋势", "新闻", "发布", "天气", "价格", "哪里买"]

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

    async def classify(self, query: str) -> IntentResult:
        """
        Two-layer intent classification:
        1. Keyword matching with confidence scoring
        2. LLM fallback if confidence < threshold
        """
        # Layer 1: Keyword Matching
        product_score = sum(1 for k in self.PRODUCT_KEYWORDS if k in query)
        external_score = sum(1 for k in self.EXTERNAL_KEYWORDS if k in query)
        
        total_len = len(query)
        # Normalize score (simple heuristic)
        confidence = 0.0
        intent = IntentType.GENERAL_CHAT
        
        if external_score > 0:
            intent = IntentType.EXTERNAL_KNOWLEDGE
            confidence = 0.8 + (0.1 * external_score)
        elif product_score > 0:
            intent = IntentType.PRODUCT_KNOWLEDGE
            confidence = 0.7 + (0.1 * product_score)
        else:
            # Default to general chat with low confidence if no keywords found
            confidence = 0.4

        if confidence >= self.CONFIDENCE_THRESHOLD:
            return IntentResult(intent=intent, confidence=min(confidence, 1.0), used_llm_fallback=False)
        
        # Layer 2: LLM Fallback
        if self.client:
            return await self._llm_classify(query)
        
        return IntentResult(intent=IntentType.GENERAL_CHAT, confidence=0.5, used_llm_fallback=False)

    async def _llm_classify(self, query: str) -> IntentResult:
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an intent classifier for a skincare AI assistant. Classify the user query into one of these categories:\n"
                                                  "- PRODUCT_KNOWLEDGE: Questions about skincare products, ingredients, routines, or advice.\n"
                                                  "- EXTERNAL_KNOWLEDGE: Questions requiring real-time info (news, latest trends, prices, weather) or specific non-skincare facts.\n"
                                                  "- GENERAL_CHAT: Greetings, casual conversation, or questions not related to skincare.\n\n"
                                                  "Reply ONLY with the category name."},
                    {"role": "user", "content": query}
                ],
                temperature=0,
                max_tokens=20
            )
            intent_str = response.choices[0].message.content.strip()
            
            # Map response to Enum
            if "PRODUCT" in intent_str:
                return IntentResult(intent=IntentType.PRODUCT_KNOWLEDGE, confidence=0.95, used_llm_fallback=True)
            elif "EXTERNAL" in intent_str:
                return IntentResult(intent=IntentType.EXTERNAL_KNOWLEDGE, confidence=0.95, used_llm_fallback=True)
            else:
                return IntentResult(intent=IntentType.GENERAL_CHAT, confidence=0.95, used_llm_fallback=True)
                
        except Exception:
            # Fallback on error
            return IntentResult(intent=IntentType.GENERAL_CHAT, confidence=0.0, used_llm_fallback=True)
