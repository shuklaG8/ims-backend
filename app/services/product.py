from typing import List, Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.product import Product
from app.repositories.product import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate

class ProductService:
    def __init__(self, db: AsyncSession):
        self.repository = ProductRepository(db)

    async def create_product(self, schema: ProductCreate) -> Product:
        # Check SKU uniqueness
        existing = await self.repository.get_by_sku(schema.sku)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with SKU '{schema.sku}' already exists."
            )
        
        product = Product(
            name=schema.name,
            sku=schema.sku.upper().strip(),
            description=schema.description,
            price=schema.price,
            stock_quantity=schema.stock_quantity
        )
        created = await self.repository.create(product)
        await self.repository.db.commit()
        return created

    async def update_product(self, id: int, schema: ProductUpdate) -> Product:
        product = await self.repository.get(id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {id} not found."
            )

        if schema.sku is not None:
            existing = await self.repository.get_by_sku(schema.sku)
            if existing and existing.id != id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product with SKU '{schema.sku}' already exists."
                )
            product.sku = schema.sku.upper().strip()

        if schema.name is not None:
            product.name = schema.name
        if schema.description is not None:
            product.description = schema.description
        if schema.price is not None:
            product.price = schema.price
        if schema.stock_quantity is not None:
            product.stock_quantity = schema.stock_quantity

        updated = await self.repository.update(product)
        await self.repository.db.commit()
        return updated

    async def delete_product(self, id: int) -> bool:
        product = await self.repository.get(id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {id} not found."
            )
        try:
            deleted = await self.repository.delete(id)
            await self.repository.db.commit()
            return deleted
        except Exception as e:
            await self.repository.db.rollback()
            # Handle DB integrity exceptions, e.g. if the product is in order items
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete product because it is referenced in one or more orders."
            )

    async def get_product(self, id: int) -> Product:
        product = await self.repository.get(id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {id} not found."
            )
        return product

    async def get_products(
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
        return await self.repository.get_filtered(
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
