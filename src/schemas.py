from typing import List, Union

from pydantic import BaseModel, Field

from datetime import datetime

class ProductBase(BaseModel):
    title: str
    images: Union[str, None] = None
    description: Union[str, None] = None
    sku: int
    gtin13: int
    brand: str
    price: int
    currency: str
    in_stock: int
    
class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    product_id: int = Field(alias="_id")
    added_at: datetime
    
    class Config:
        orm_mode = True