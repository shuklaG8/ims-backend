from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    sku: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    price: float = Field(..., ge=0.0, description="Price must be non-negative")
    stock_quantity: int = Field(..., ge=0, description="Stock must be non-negative")

    @field_validator('sku')
    @classmethod
    def clean_sku(cls, v: str) -> str:
        return v.strip().upper()

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    sku: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0.0)
    stock_quantity: Optional[int] = Field(None, ge=0)

    @field_validator('sku')
    @classmethod
    def clean_sku(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return v.strip().upper()
        return v

class ProductOut(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ProductPagination(BaseModel):
    items: list[ProductOut]
    total: int
    skip: int
    limit: int
