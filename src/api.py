from typing import Union, List
from fastapi import FastAPI
from pydantic import BaseModel, Field
from datetime import datetime
from db_connect import *
import json
import configparser
from pymongo import MongoClient
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


config = configparser.ConfigParser()
config.read('config.conf')
mongoDB = connect_to_mongo(config['mongo_db']['name'],config['mongo_db']['password'])

app = FastAPI()

class OID(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        try:
            return ObjectId(str(v))
        except InvalidId:
            raise ValueError("Not a valid ObjectId")

class Product(BaseModel):
    product_id: int = Field(alias="_id")
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

@app.get("/products/", response_model=List[Product])
def read_item():
    query = mongoDB.products.find()
    return [q for q in query]

@app.get("/products/{product_id}", response_model=Product)
def read_item(product_id: int):
    query = mongoDB.products.find({"_id" : product_id})
    return query[0]

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