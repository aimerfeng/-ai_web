from pydantic import BaseModel
from enum import Enum

class SkinType(str, Enum):
    OILY = "oily"
    DRY = "dry"
    COMBINATION = "combination"
    SENSITIVE = "sensitive"
    NORMAL = "normal"

class BudgetRange(str, Enum):
    BUDGET = "budget"
    MID_RANGE = "mid-range"
    LUXURY = "luxury"

class Product(BaseModel):
    id: str
    product_name: str
    brand: str
    core_ingredients: list[str]
    suitable_skin_types: list[SkinType]
    efficacy: list[str]
    risk_ingredients: list[str]
    price_range: BudgetRange
    
class ProductDocument(BaseModel):
    """Schema for product data stored in ChromaDB."""
    id: str
    text: str  # Formatted string for embedding
    metadata: dict  # Original product fields for retrieval
