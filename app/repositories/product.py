from typing import List, Optional, Tuple
from sqlalchemy import select, func, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.product import Product
from app.repositories.base import BaseRepository

class ProductRepository(BaseRepository[Product]):
    def __init__(self, db: AsyncSession):
        super().__init__(Product, db)

    async def get_by_sku(self, sku: str) -> Optional[Product]:
        query = select(Product).where(Product.sku == sku.upper().strip())
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_filtered(
        self,
        *,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_stock: Optional[int] = None,
        max_stock: Optional[int] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[Product], int]:
        # Base query for selecting items
        query = select(Product)

        # Filters
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    Product.name.ilike(search_pattern),
                    Product.sku.ilike(search_pattern),
                    Product.description.ilike(search_pattern)
                )
            )
        if min_price is not None:
            query = query.where(Product.price >= min_price)
        if max_price is not None:
            query = query.where(Product.price <= max_price)
        if min_stock is not None:
            query = query.where(Product.stock_quantity >= min_stock)
        if max_stock is not None:
            query = query.where(Product.stock_quantity <= max_stock)

        # Count total matches before pagination
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total_count = count_result.scalar_one_or_none() or 0

        # Sorting
        sort_column = getattr(Product, sort_by, Product.created_at)
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        # Pagination
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all()), total_count
