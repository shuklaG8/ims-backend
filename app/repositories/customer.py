from typing import List, Optional, Tuple
from sqlalchemy import select, func, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.customer import Customer
from app.repositories.base import BaseRepository

class CustomerRepository(BaseRepository[Customer]):
    def __init__(self, db: AsyncSession):
        super().__init__(Customer, db)

    async def get_by_email(self, email: str) -> Optional[Customer]:
        query = select(Customer).where(Customer.email == email.lower().strip())
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_filtered(
        self,
        *,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[Customer], int]:
        query = select(Customer)

        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    Customer.name.ilike(search_pattern),
                    Customer.email.ilike(search_pattern),
                    Customer.phone.ilike(search_pattern)
                )
            )

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total_count = count_result.scalar_one_or_none() or 0

        # Sorting
        sort_column = getattr(Customer, sort_by, Customer.created_at)
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        # Pagination
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all()), total_count
