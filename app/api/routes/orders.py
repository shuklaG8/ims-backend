from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.db.session import get_db
from app.schemas.order import OrderCreate, OrderOut, OrderPagination
from app.services.order import OrderService

router = APIRouter()

@router.get("", response_model=OrderPagination)
async def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    customer_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db)
):
    service = OrderService(db)
    items, total = await service.get_orders(
        skip=skip,
        limit=limit,
        customer_id=customer_id,
        status=status,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/{id}", response_model=OrderOut)
async def get_order(id: int, db: AsyncSession = Depends(get_db)):
    service = OrderService(db)
    return await service.get_order(id)

@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(schema: OrderCreate, db: AsyncSession = Depends(get_db)):
    service = OrderService(db)
    return await service.create_order(schema)
