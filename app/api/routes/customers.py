from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.db.session import get_db
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerOut, CustomerPagination
from app.services.customer import CustomerService

router = APIRouter()

@router.get("", response_model=CustomerPagination)
async def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db)
):
    service = CustomerService(db)
    items, total = await service.get_customers(
        skip=skip,
        limit=limit,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/{id}", response_model=CustomerOut)
async def get_customer(id: int, db: AsyncSession = Depends(get_db)):
    service = CustomerService(db)
    return await service.get_customer(id)

@router.post("", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
async def create_customer(schema: CustomerCreate, db: AsyncSession = Depends(get_db)):
    service = CustomerService(db)
    return await service.create_customer(schema)

@router.put("/{id}", response_model=CustomerOut)
async def update_customer(id: int, schema: CustomerUpdate, db: AsyncSession = Depends(get_db)):
    service = CustomerService(db)
    return await service.update_customer(id, schema)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(id: int, db: AsyncSession = Depends(get_db)):
    service = CustomerService(db)
    await service.delete_customer(id)
    return None
