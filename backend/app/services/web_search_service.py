from typing import List
from pydantic import BaseModel
from tavily import TavilyClient, AsyncTavilyClient
from app.core.config import settings

class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str

class WebSearchService:
    def __init__(self):
        self.client = AsyncTavilyClient(api_key=settings.TAVILY_API_KEY) if settings.TAVILY_API_KEY else None

    async def search(self, query: str, max_results: int = 3) -> List[SearchResult]:
        """Search web using Tavily API."""
        if not self.client:
            return []
            
        try:
            response = await self.client.search(
                query=query,
                max_results=max_results,
                search_depth="basic"
            )
            
            results = []
            for result in response.get("results", []):
                results.append(SearchResult(
                    title=result.get("title", ""),
                    url=result.get("url", ""),
                    snippet=result.get("content", "")
                ))
            return results
        except Exception as e:
            print(f"Web search failed: {e}")
            return []
