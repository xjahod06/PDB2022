from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

class Product(BaseModel):
    product_id: int
    title: str
    images: Union[str, None] = None
    description: Union[str, None] = None
    sku: int
    gtin13: int
    brand: str
    price: int
    currency: str
    in_stock: int
    added_at: datetime
    
@app.post("/products/")
def read_item(product: Product):
    pass
    return product

@app.get("/products/{product_id}", response_model=Product)
def read_item(product_id: int):
    pass
    #TODO replace with product model
    return {"product_id" : product_id,
            "title" : title,
            "images" : images,
            "description" : description,
            "sku" : sku,
            "gtin13" : gtin13,
            "brand" : brand,
            "price" : price,
            "currency" : currency,
            "in_stock" : in_stock,
            "added_at" : added_at
            }

@app.put("/products/{product_id}", response_model=Product)
def read_item(product_id: int, product: Product):
    pass
    return product

@app.delete("/products/{product_id}")
def read_item():
    pass
    return 200

@app.get("/price/")
def read_item(price: int):
    pass
    #TODO přesná cena (asi useless ?)
    return None

@app.get("/priceRange/")
def read_item(gt: Union[int,None] = 0,lt: Union[int,None] = None):
    pass
    #TODO rozsah cen
    return None

@app.get("/addedAt/")
def read_item(time: datetime):
    pass
    #TODO přesné datum přidání produktu (asi useless ?)
    return None

@app.get("/addedAtRange/")
def read_item(gt: Union[datetime,None] = 0,lt: Union[datetime,None] = None):
    pass
    #TODO rozsad podle data přidání produktu
    return None

@app.get("/inStockRange/")
def read_item(gt: Union[int,None] = 0, lt: Union[int,None] = None):
    pass
    #TODO podle rozmezí počtu produktů na skladě
    return None

@app.get("/category/{category}")
def read_item(category: str):
    pass
    #TODO categorie jsou v sku tak to rozkličovat a vratit
    return None

@app.get("/brand/{brand}")
def read_item(brand: str):
    pass
    #TODO vyhledavani podle značek
    return None

@app.get("/inDescription/{key_word}")
def read_item(key_word: str):
    pass
    #TODO filtrovat podle klíčových slov v popisu produktu
    return None