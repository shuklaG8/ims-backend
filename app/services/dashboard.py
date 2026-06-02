from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.product import Product
from app.models.customer import Customer
from app.models.order import Order
from typing import Dict, Any, List

class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_stats(self) -> Dict[str, Any]:
        # Total Products count
        p_count_query = select(func.count(Product.id))
        p_count_result = await self.db.execute(p_count_query)
        total_products = p_count_result.scalar_one_or_none() or 0

        # Total Customers count
        c_count_query = select(func.count(Customer.id))
        c_count_result = await self.db.execute(c_count_query)
        total_customers = c_count_result.scalar_one_or_none() or 0

        # Total Orders count
        o_count_query = select(func.count(Order.id))
        o_count_result = await self.db.execute(o_count_query)
        total_orders = o_count_result.scalar_one_or_none() or 0

        # Total Revenue (sum of total_amount of all orders)
        revenue_query = select(func.sum(Order.total_amount))
        revenue_result = await self.db.execute(revenue_query)
        total_revenue = revenue_result.scalar_one_or_none() or 0.0

        # Low stock products (stock_quantity <= 10)
        low_stock_query = select(Product).where(Product.stock_quantity <= 10).order_by(Product.stock_quantity.asc()).limit(10)
        low_stock_result = await self.db.execute(low_stock_query)
        low_stock_products = list(low_stock_result.scalars().all())

        return {
            "total_products": total_products,
            "total_customers": total_customers,
            "total_orders": total_orders,
            "total_revenue": float(total_revenue),
            "low_stock_products": [
                {
                    "id": p.id,
                    "name": p.name,
                    "sku": p.sku,
                    "price": p.price,
                    "stock_quantity": p.stock_quantity
                } for p in low_stock_products
            ]
        }
