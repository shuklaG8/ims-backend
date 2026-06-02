from typing import List, Optional, Tuple
from sqlalchemy import select, func, desc, asc
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.order import Order, OrderItem
from app.repositories.base import BaseRepository

class OrderRepository(BaseRepository[Order]):
    def __init__(self, db: AsyncSession):
        super().__init__(Order, db)

    async def get_by_id(self, order_id: int) -> Optional[Order]:
        # Eager load customer and order items + their associated product
        query = (
            select(Order)
            .where(Order.id == order_id)
            .options(
                joinedload(Order.customer),
                selectinload(Order.items).joinedload(OrderItem.product)
            )
        )
        result = await self.db.execute(query)
        return result.unique().scalars().first()

    async def get_filtered(
        self,
        *,
        skip: int = 0,
        limit: int = 10,
        customer_id: Optional[int] = None,
        status: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[Order], int]:
        # Base query with joined customer loading
        query = select(Order).options(joinedload(Order.customer))

        if customer_id is not None:
            query = query.where(Order.customer_id == customer_id)
        if status:
            query = query.where(Order.status == status)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total_count = count_result.scalar_one_or_none() or 0

        # Sorting
        sort_column = getattr(Order, sort_by, Order.created_at)
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        # Pagination
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.unique().scalars().all()), total_count
