from typing import List, Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.customer import Customer
from app.repositories.customer import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate

class CustomerService:
    def __init__(self, db: AsyncSession):
        self.repository = CustomerRepository(db)

    async def create_customer(self, schema: CustomerCreate) -> Customer:
        # Check email uniqueness
        existing = await self.repository.get_by_email(schema.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Customer with email '{schema.email}' already exists."
            )
        
        customer = Customer(
            name=schema.name,
            email=schema.email.lower().strip(),
            phone=schema.phone,
            address=schema.address
        )
        return await self.repository.create(customer)

    async def update_customer(self, id: int, schema: CustomerUpdate) -> Customer:
        customer = await self.repository.get(id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {id} not found."
            )

        if schema.email is not None:
            existing = await self.repository.get_by_email(schema.email)
            if existing and existing.id != id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Customer with email '{schema.email}' already exists."
                )
            customer.email = schema.email.lower().strip()

        if schema.name is not None:
            customer.name = schema.name
        if schema.phone is not None:
            customer.phone = schema.phone
        if schema.address is not None:
            customer.address = schema.address

        return await self.repository.update(customer)

    async def delete_customer(self, id: int) -> bool:
        customer = await self.repository.get(id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {id} not found."
            )
        try:
            return await self.repository.delete(id)
        except Exception as e:
            # Handle DB integrity exceptions, e.g. if the customer has placed orders
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete customer because they have active or past orders."
            )

    async def get_customer(self, id: int) -> Customer:
        customer = await self.repository.get(id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {id} not found."
            )
        return customer

    async def get_customers(
        self,
        *,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[Customer], int]:
        return await self.repository.get_filtered(
            skip=skip,
            limit=limit,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order
        )
