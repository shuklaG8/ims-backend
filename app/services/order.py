from typing import List, Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.customer import Customer
from app.repositories.order import OrderRepository
from app.repositories.product import ProductRepository
from app.repositories.customer import CustomerRepository
from app.schemas.order import OrderCreate

class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.order_repo = OrderRepository(db)
        self.product_repo = ProductRepository(db)
        self.customer_repo = CustomerRepository(db)

    async def create_order(self, schema: OrderCreate) -> Order:
        # Validate Customer Exists
        customer = await self.customer_repo.get(schema.customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {schema.customer_id} not found."
            )

        # Run inside transaction block
        # Using db.begin_nested() or relying on outer session transaction handling.
        # Since we might call db.commit() in the controller, or we want the transaction here:
        # Let's run with self.db.begin_nested() to allow rollback if any item fails, 
        # but since we want standard transaction:
        try:
            # We'll use a nested transaction (savepoint) or just normal transaction flow.
            # If we are using FastAPI dependencies, the outer middleware/handler will commit or we commit it here.
            # Let's commit explicitly in the service so we control the transaction.
            async with self.db.begin_nested():
                total_amount = 0.0
                order_items_to_create = []

                # Group duplicate products in the request to validate total quantity requested for each product
                product_quantities = {}
                for item in schema.items:
                    product_quantities[item.product_id] = product_quantities.get(item.product_id, 0) + item.quantity

                # Fetch products and validate stock
                for product_id, quantity in product_quantities.items():
                    # Select for update to lock the rows for concurrency safety
                    query = select(Product).where(Product.id == product_id).with_for_update()
                    res = await self.db.execute(query)
                    product = res.scalars().first()

                    if not product:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Product with ID {product_id} not found."
                        )

                    # Validate stock
                    if product.stock_quantity < quantity:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=(
                                f"Insufficient stock for product '{product.name}' (SKU: {product.sku}). "
                                f"Available: {product.stock_quantity}, Requested: {quantity}."
                            )
                        )

                    # Reduce inventory
                    product.stock_quantity -= quantity
                    await self.product_repo.update(product)

                    # Calculate price contribution
                    item_total_price = product.price * quantity
                    total_amount += item_total_price

                    # Prepare order item
                    order_items_to_create.append({
                        "product_id": product_id,
                        "quantity": quantity,
                        "unit_price": product.price
                    })

                # Create Order
                order = Order(
                    customer_id=schema.customer_id,
                    total_amount=total_amount,
                    status="completed"  # orders are marked completed since stock is reduced immediately
                )
                self.db.add(order)
                await self.db.flush()  # gets the order ID

                # Create Order Items and link
                for item_data in order_items_to_create:
                    item = OrderItem(
                        order_id=order.id,
                        product_id=item_data["product_id"],
                        quantity=item_data["quantity"],
                        unit_price=item_data["unit_price"]
                    )
                    self.db.add(item)
                
                await self.db.flush()

            # Commit the outer transaction
            await self.db.commit()

            # Refresh and return the full order
            return await self.order_repo.get_by_id(order.id)

        except HTTPException as he:
            # Rollback is automatic with db.begin_nested() when an exception is raised
            raise he
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating order: {str(e)}"
            )

    async def get_order(self, order_id: int) -> Order:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with ID {order_id} not found."
            )
        return order

    async def get_orders(
        self,
        *,
        skip: int = 0,
        limit: int = 10,
        customer_id: Optional[int] = None,
        status: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[Order], int]:
        return await self.order_repo.get_filtered(
            skip=skip,
            limit=limit,
            customer_id=customer_id,
            status=status,
            sort_by=sort_by,
            sort_order=sort_order
        )
