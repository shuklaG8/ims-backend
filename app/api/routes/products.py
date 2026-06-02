from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.db.session import get_db
from app.schemas.product import ProductCreate, ProductUpdate, ProductOut, ProductPagination
from app.services.product import ProductService

router = APIRouter()

@router.get("", response_model=ProductPagination)
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None, ge=0.0),
    max_price: Optional[float] = Query(None, ge=0.0),
    min_stock: Optional[int] = Query(None, ge=0),
    max_stock: Optional[int] = Query(None, ge=0),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db)
):
    service = ProductService(db)
    items, total = await service.get_products(
        skip=skip,
        limit=limit,
        search=search,
        min_price=min_price,
        max_price=max_price,
        min_stock=min_stock,
        max_stock=max_stock,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/{id}", response_model=ProductOut)
async def get_product(id: int, db: AsyncSession = Depends(get_db)):
    service = ProductService(db)
    return await service.get_product(id)

@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product(schema: ProductCreate, db: AsyncSession = Depends(get_db)):
    service = ProductService(db)
    return await service.create_product(schema)

@router.put("/{id}", response_model=ProductOut)
async def update_product(id: int, schema: ProductUpdate, db: AsyncSession = Depends(get_db)):
    service = ProductService(db)
    return await service.update_product(id, schema)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(id: int, db: AsyncSession = Depends(get_db)):
    service = ProductService(db)
    await service.delete_product(id)
    return None
