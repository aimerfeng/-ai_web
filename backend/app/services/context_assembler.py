from datetime import datetime
from typing import List, Dict, Any
from app.models.user import UserProfile, Message
from app.schemas.product import Product
from app.services.web_search_service import SearchResult

class ContextAssembler:
    SYSTEM_PROMPT = """You are SkinTech AI Consultant, a professional cosmetic chemist and skincare formulator ("配方师").
Your goal is to provide personalized, science-backed skincare advice.

**Persona Guidelines:**
- Tone: Professional, empathetic, scientific yet accessible.
- Perspective: Analyze ingredients, formulations, and skin physiology.
- Constraints: Do NOT provide medical diagnoses. Recommend consulting a dermatologist for serious conditions.
- Context: Use the provided product knowledge base and user profile to tailor your advice.

**Response Structure:**
1. Direct Answer: Address the user's question immediately.
2. Scientific Rationale: Explain WHY based on ingredients/skin type.
3. Product Recommendations (if applicable): Use the retrieved products.
4. Usage Advice: How to incorporate into routine.

**Current Context:**
{time_context}
"""

    def assemble(
        self,
        current_query: str,
        rag_products: List[Product] | None,
        web_results: List[SearchResult] | None,
        user_profile: UserProfile | None,
        chat_history: List[Message],
        max_tokens: int = 4096  # Approximation for context window management
    ) -> List[Dict[str, str]]:
        
        # 1. System Prompt with Time
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        system_content = self.SYSTEM_PROMPT.format(time_context=f"Current System Time: {time_str}")
        
        # 2. User Profile Context
        profile_str = ""
        if user_profile:
            profile_str = f"""
**User Profile:**
- Skin Type: {user_profile.skin_type or 'Unknown'}
- Sensitivities: {', '.join(user_profile.sensitivities) if user_profile.sensitivities else 'None'}
- Concerns: {', '.join(user_profile.concerns) if user_profile.concerns else 'None'}
- Budget: {user_profile.budget_range or 'Unknown'}
"""

        # 3. RAG / Web Context
        knowledge_str = ""
        if rag_products:
            products_text = "\n".join([
                f"- {p.product_name} ({p.brand}): {', '.join(p.core_ingredients)}. Good for {', '.join([s.value for s in p.suitable_skin_types])}."
                for p in rag_products
            ])
            knowledge_str += f"\n**Retrieved Product Knowledge:**\n{products_text}\n"
            
        if web_results:
            web_text = "\n".join([
                f"- {r.title} ({r.url}): {r.snippet}" 
                for r in web_results
            ])
            knowledge_str += f"\n**Web Search Results:**\n{web_text}\n"

        # 4. Construct Messages
        messages = [{"role": "system", "content": system_content}]
        
        # Inject Context into System or First Message
        context_block = f"{profile_str}\n{knowledge_str}"
        if context_block.strip():
            messages.append({"role": "system", "content": f"Context Information:{context_block}"})

        # 5. Chat History (Short Term Memory) - Limit to last 10
        # Simple token management: just take last 10 for now. 
        # For strict token budgeting, we would count tokens and truncate.
        recent_history = chat_history[-10:]
        for msg in recent_history:
            messages.append({"role": msg.role, "content": msg.content})
            
        # 6. Current Query
        messages.append({"role": "user", "content": current_query})
        
        return messages
