from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.schemas.product import ProductOut
from app.schemas.customer import CustomerOut

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=1, description="Quantity must be at least 1")

class OrderItemOut(BaseModel):
    id: int
    order_id: int
    product_id: int
    quantity: int
    unit_price: float
    product: Optional[ProductOut] = None

    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    customer_id: int
    items: List[OrderItemCreate] = Field(..., min_length=1, description="Order must contain at least one item")

class OrderOut(BaseModel):
    id: int
    customer_id: int
    total_amount: float
    status: str
    created_at: datetime
    items: List[OrderItemOut]
    customer: Optional[CustomerOut] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class OrderPagination(BaseModel):
    items: List[OrderOut]
    total: int
    skip: int
    limit: int
