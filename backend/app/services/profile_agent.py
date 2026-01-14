import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from openai import AsyncOpenAI
from app.core.config import settings
from app.models.user import UserProfile, Message, User

class ProfileExtractionAgent:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

    async def extract_and_update(self, user_id: str, chat_history: list[Message]) -> None:
        """
        Analyze conversation history and update user profile.
        """
        if not self.client or not chat_history:
            return

        # Prepare context for LLM
        history_text = "\n".join([f"{msg.role}: {msg.content}" for msg in chat_history[-20:]]) # Analyze last 20 messages
        
        system_prompt = """You are a profile extraction agent. Your job is to analyze the conversation and extract user skincare preferences.
Output JSON ONLY with the following keys (if information is found, otherwise leave null/empty list):
- skin_type: "oily", "dry", "combination", "sensitive", "normal" (or null)
- sensitivities: list of strings (e.g. ["alcohol", "fragrance"])
- preferred_brands: list of strings
- budget_range: "budget", "mid-range", "luxury" (or null)
- concerns: list of strings (e.g. ["acne", "aging"])

Example Output:
{
  "skin_type": "oily",
  "sensitivities": [],
  "preferred_brands": ["CeraVe"],
  "budget_range": "budget",
  "concerns": ["acne"]
}
"""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Conversation:\n{history_text}"}
                ],
                response_format={"type": "json_object"},
                temperature=0
            )
            
            extracted_data = json.loads(response.choices[0].message.content)
            await self._update_profile_in_db(user_id, extracted_data)
            
        except Exception as e:
            print(f"Profile extraction failed: {e}")

    async def _update_profile_in_db(self, user_id: str, data: dict) -> None:
        """Atomically update user profile."""
        # Check if profile exists
        result = await self.db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
        profile = result.scalar_one_or_none()
        
        if not profile:
            profile = UserProfile(user_id=user_id)
            self.db.add(profile)
        
        # Merge data (simple overwrite for now, but could be smarter)
        if data.get("skin_type"):
            profile.skin_type = data["skin_type"]
        
        if data.get("budget_range"):
            profile.budget_range = data["budget_range"]
            
        # For lists, we might want to append unique values instead of overwrite
        # But for simplicity in this MVP, let's merge unique items
        if data.get("sensitivities"):
            current = set(profile.sensitivities or [])
            current.update(data["sensitivities"])
            profile.sensitivities = list(current)
            
        if data.get("preferred_brands"):
            current = set(profile.preferred_brands or [])
            current.update(data["preferred_brands"])
            profile.preferred_brands = list(current)
            
        if data.get("concerns"):
            current = set(profile.concerns or [])
            current.update(data["concerns"])
            profile.concerns = list(current)
            
        profile.version += 1
        await self.db.commit()
