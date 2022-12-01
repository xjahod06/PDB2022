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
    price: float
    currency: str
    in_stock: int


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    title: Union[str, None] = None
    sku: Union[int, None] = None
    gtin13: Union[int, None] = None
    brand: Union[str, None] = None
    price: Union[float, None] = None
    currency: Union[str, None] = None
    in_stock: Union[int, None] = None


class Product(ProductBase):
    _id: int = Field(alias="product_id")
    added_at: datetime

    class Config:
        orm_mode = True
        
class OrderBase(BaseModel):
    price : int
    user_information : str
    transport_information : str
    status : str
    query : str
    
class OrderCreate(OrderBase):
    pass
    
class Order(OrderBase):
    _id : int
    created_at : int
    
    class Config:
        orm_mode = True
