import json
import uuid
import random
from faker import Faker
from app.schemas.product import Product, SkinType, BudgetRange
from app.core.vector_db import get_collection
from typing import List
import asyncio

fake = Faker("zh_CN")

class IngestionService:
    # 真实品牌列表
    BRANDS = [
        "SK-II", "La Mer", "Estee Lauder (雅诗兰黛)", "Lancome (兰蔻)", "Kiehl's (科颜氏)", 
        "The Ordinary", "CeraVe (适乐肤)", "La Roche-Posay (理肤泉)", "Shiseido (资生堂)", 
        "Clarins (娇韵诗)", "Winona (薇诺娜)", "Proya (珀莱雅)", "SkinCeuticals (修丽可)",
        "Neutrogena (露得清)", "HBN", "Dr.Ci:Labo (城野医生)"
    ]
    
    # 真实成分与功效映射
    INGREDIENTS_MAP = {
        "烟酰胺 (Niacinamide)": ["美白", "控油", "修复屏障"],
        "视黄醇 (Retinol/A醇)": ["抗老", "淡纹", "祛痘"],
        "透明质酸 (Hyaluronic Acid)": ["保湿", "补水"],
        "维生素C (Vitamin C)": ["抗氧化", "提亮肤色"],
        "水杨酸 (Salicylic Acid)": ["去角质", "疏通毛孔", "祛痘"],
        "神经酰胺 (Ceramides)": ["修复屏障", "保湿"],
        "胜肽 (Peptides)": ["抗老", "紧致"],
        "积雪草 (Centella Asiatica)": ["舒缓", "抗炎", "修复"],
        "二裂酵母 (Bifida Ferment Lysate)": ["修复", "抗老"],
        "玻色因 (Pro-Xylane)": ["抗老", "紧致", "充盈"],
        "壬二酸 (Azelaic Acid)": ["祛痘", "美白", "消炎"],
        "果酸 (AHA)": ["去角质", "嫩肤"],
        "角鲨烷 (Squalane)": ["保湿", "修复"],
        "依克多因 (Ectoin)": ["防护", "保湿", "抗炎"]
    }

    PRODUCT_TYPES = ["面霜", "精华", "爽肤水", "洁面乳", "防晒霜", "眼霜", "面膜"]

    RISKS = ["酒精 (Alcohol)", "香精 (Fragrance)", "防腐剂 (Parabens)", "矿物油 (Mineral Oil)"]

    def generate_products(self, count: int = 1000) -> List[Product]:
        """Generate realistic skincare product data."""
        products = []
        ingredients_list = list(self.INGREDIENTS_MAP.keys())
        
        for _ in range(count):
            brand = random.choice(self.BRANDS)
            p_type = random.choice(self.PRODUCT_TYPES)
            
            # Select core ingredients
            num_ingredients = random.randint(1, 3)
            core_ingredients = random.sample(ingredients_list, k=num_ingredients)
            
            # Derive efficacy from ingredients
            efficacy_set = set()
            for ing in core_ingredients:
                efficacy_set.update(self.INGREDIENTS_MAP[ing])
            efficacy = list(efficacy_set)
            
            # Generate Name
            main_ing_name = core_ingredients[0].split("(")[0].strip()
            product_name = f"{brand} {main_ing_name} {p_type}"
            
            # Determine skin types based on ingredients/type
            # Logic: Salicylic acid -> Oily; Ceramides -> Dry/Sensitive
            suitable_skin_types = []
            if "水杨酸" in str(core_ingredients) or "控油" in str(efficacy):
                suitable_skin_types.extend([SkinType.OILY, SkinType.COMBINATION])
            elif "神经酰胺" in str(core_ingredients) or "角鲨烷" in str(core_ingredients):
                suitable_skin_types.extend([SkinType.DRY, SkinType.SENSITIVE, SkinType.NORMAL])
            else:
                suitable_skin_types = random.sample(list(SkinType), k=random.randint(2, 4))
            
            # Unique
            suitable_skin_types = list(set(suitable_skin_types))

            # Risks
            risk_ingredients = []
            if random.random() > 0.8:
                risk_ingredients = random.sample(self.RISKS, k=1)
            
            # Price
            if brand in ["La Mer", "SK-II", "SkinCeuticals", "Estee Lauder (雅诗兰黛)", "Lancome (兰蔻)"]:
                price_range = BudgetRange.LUXURY
            elif brand in ["CeraVe (适乐肤)", "The Ordinary", "Neutrogena (露得清)"]:
                price_range = BudgetRange.BUDGET
            else:
                price_range = BudgetRange.MID_RANGE

            product = Product(
                id=str(uuid.uuid4()),
                product_name=product_name,
                brand=brand,
                core_ingredients=core_ingredients,
                suitable_skin_types=suitable_skin_types,
                efficacy=efficacy,
                risk_ingredients=risk_ingredients,
                price_range=price_range
            )
            products.append(product)
        return products

    def format_for_embedding(self, product: Product) -> str:
        """Format product into standardized text template for embedding."""
        return (
            f"产品名称: {product.product_name}\n"
            f"品牌: {product.brand}\n"
            f"核心成分: {', '.join(product.core_ingredients)}\n"
            f"功效: {', '.join(product.efficacy)}\n"
            f"适用肤质: {', '.join([st.value for st in product.suitable_skin_types])}\n"
            f"风险成分/注意事项: {', '.join(product.risk_ingredients) if product.risk_ingredients else '无'}\n"
            f"价格定位: {product.price_range.value}"
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
        
        # ChromaDB metadata values must be str, int, float, bool. Not list.
        # We need to serialize lists to strings.
        metadatas = []
        for p in products:
            meta = p.model_dump(mode='json')
            # Convert list fields to strings
            for key, value in meta.items():
                if isinstance(value, list):
                    meta[key] = json.dumps(value, ensure_ascii=False)
            metadatas.append(meta)
        
        batch_size = 100
        for i in range(0, len(products), batch_size):
            end = min(i + batch_size, len(products))
            collection.upsert(
                ids=ids[i:end],
                documents=documents[i:end],
                metadatas=metadatas[i:end]
            )
            print(f"Ingested batch {i} to {end}")
            
        return len(products)

if __name__ == "__main__":
    async def main():
        service = IngestionService()
        print("正在生成增强版美妆数据...")
        products = service.generate_products(2000) # Generate 2000 realistic products
        print(f"生成了 {len(products)} 个产品。")
        
        print("保存到 JSON...")
        service.save_to_json(products, "products_data_enhanced.json")
        
        print("正在存入 ChromaDB (RAG)...")
        count = await service.ingest(products)
        print(f"成功存入 {count} 个产品到知识库。")
        
    asyncio.run(main())