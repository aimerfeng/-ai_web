import json
import uuid
import random
from faker import Faker
from app.schemas.product import Product, SkinType, BudgetRange
from app.core.vector_db import get_collection
from typing import List

fake = Faker("zh_CN")

class IngestionService:
    BRANDS = ["SK-II", "La Mer", "Estee Lauder", "Lancome", "Kiehl's", "The Ordinary", "CeraVe", "La Roche-Posay", "Shiseido", "Clarins"]
    INGREDIENTS = ["Niacinamide", "Retinol", "Hyaluronic Acid", "Vitamin C", "Salicylic Acid", "Ceramides", "Peptides", "Snail Mucin", "Centella Asiatica", "Tea Tree Oil"]
    EFFICACIES = ["Moisturizing", "Anti-aging", "Brightening", "Acne Control", "Soothing", "Exfoliating", "Sun Protection"]
    RISKS = ["Alcohol", "Fragrance", "Parabens", "Sulfates", "Essential Oils"]

    def generate_products(self, count: int = 5000) -> List[Product]:
        """Generate mock skincare product data."""
        products = []
        for _ in range(count):
            product = Product(
                id=str(uuid.uuid4()),
                product_name=f"{random.choice(self.BRANDS)} {fake.word()} {random.choice(['Cream', 'Serum', 'Toner', 'Cleanser'])}",
                brand=random.choice(self.BRANDS),
                core_ingredients=random.sample(self.INGREDIENTS, k=random.randint(1, 3)),
                suitable_skin_types=random.sample(list(SkinType), k=random.randint(1, 3)),
                efficacy=random.sample(self.EFFICACIES, k=random.randint(1, 2)),
                risk_ingredients=random.sample(self.RISKS, k=random.randint(0, 1)) if random.random() > 0.7 else [],
                price_range=random.choice(list(BudgetRange))
            )
            products.append(product)
        return products

    def format_for_embedding(self, product: Product) -> str:
        """Format product into standardized text template for embedding."""
        return (
            f"Product: {product.product_name}, "
            f"Brand: {product.brand}, "
            f"Contains: {', '.join(product.core_ingredients)}, "
            f"Good for: {', '.join([st.value for st in product.suitable_skin_types])}, "
            f"Effects: {', '.join(product.efficacy)}, "
            f"Caution: {', '.join(product.risk_ingredients) if product.risk_ingredients else 'None'}, "
            f"Price: {product.price_range.value}"
        )

    def save_to_json(self, products: List[Product], filepath: str = "products_data.json") -> None:
        """Save generated products to JSON file."""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump([p.model_dump() for p in products], f, ensure_ascii=False, indent=2)

    async def ingest(self, products: List[Product]) -> int:
        """Vectorize products and upsert to ChromaDB."""
        collection = get_collection()
        
        ids = [p.id for p in products]
        documents = [self.format_for_embedding(p) for p in products]
        metadatas = [p.model_dump(mode='json') for p in products]
        
        # ChromaDB handles batching internally, but for 5000 records it's safe to send at once
        # For larger datasets, we might want to batch manually (e.g., 100 at a time)
        batch_size = 100
        for i in range(0, len(products), batch_size):
            end = min(i + batch_size, len(products))
            collection.upsert(
                ids=ids[i:end],
                documents=documents[i:end],
                metadatas=metadatas[i:end]
            )
            
        return len(products)

if __name__ == "__main__":
    # Script to run generation manually
    import asyncio
    
    async def main():
        service = IngestionService()
        print("Generating products...")
        products = service.generate_products(5000)
        print(f"Generated {len(products)} products.")
        
        print("Saving to JSON...")
        service.save_to_json(products, "backend/products_data.json")
        
        print("Ingesting to ChromaDB...")
        count = await service.ingest(products)
        print(f"Ingested {count} products successfully.")
        
    asyncio.run(main())
