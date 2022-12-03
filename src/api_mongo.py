from typing import List, Union
from fastapi import FastAPI, HTTPException

import schemas

from datetime import datetime
from db_connect import *
import configparser


config = configparser.ConfigParser()
config.read('config.conf')
mongoDB = async_connect_to_mongo(
    config['mongo_db']['name'], config['mongo_db']['password'])

app = FastAPI()


@app.get("/products/", response_model=List[schemas.Product])
async def read_item():
    query = await mongoDB.products.find().to_list(None)
    return query


@app.get("/products/{product_id}", response_model=Union[schemas.Product, None])
async def read_item(product_id: int):
    query = await mongoDB.products.find_one({"_id": product_id})
    if query:
        return query
    else:
        raise HTTPException(status_code=404, detail="Product not found")


@app.delete("/products/{product_id}", status_code=200, response_model=None)
async def read_item(product_id: int):
    result = await mongoDB.products.delete_one({"_id": product_id})
    if result.deleted_count != 1:
        raise HTTPException(status_code=404, detail="Product not found")
    else:
        return


@app.get("/priceRange/", response_model=List[schemas.Product])
async def read_item(gt: Union[float, None] = 0, lt: Union[float, None] = None):
    if lt:
        query = await mongoDB.products.find({"price": {"$gt": gt, "$lt": lt}}).to_list(None)
    else:
        query = await mongoDB.products.find({"price": {"$gt": gt}}).to_list(None)
    return query


@app.get("/addedAtRange/", response_model=List[schemas.Product])
async def read_item(gt: Union[datetime, None] = 0, lt: Union[datetime, None] = None):
    if lt:
        query = await mongoDB.products.find({"added_at": {"$gt": gt, "$lt": lt}}) \
            .to_list(None)
    else:
        query = await mongoDB.products.find({"added_at": {"$gt": gt}}).to_list(None)
    return query


@app.get("/inStockRange/", response_model=List[schemas.Product])
async def read_item(gt: Union[int, None] = 0, lt: Union[int, None] = None):
    if lt:
        query = await mongoDB.products.find({"in_stock": {"$gt": gt, "$lt": lt}}) \
            .to_list(None)
    else:
        query = await mongoDB.products.find({"in_stock": {"$gt": gt}}).to_list(None)
    return query


@app.get("/brand/{brand}", response_model=List[schemas.Product])
async def read_item(brand: str):
    query = await mongoDB.products.find({"brand": brand}).to_list(None)
    return query


@app.get("/inDescription/{key_word}", response_model=Union[schemas.Product, None])
async def read_item(key_word: str):
    query = await mongoDB.products.find_one({"description": {"$regex": key_word}})
    return query


@app.get("/orders/{order_id}", response_model=Union[schemas.Order, None])
async def read_item(order_id: int):
    query = await mongoDB.orders.find_one({'_id': order_id})
    if query:
        return query
    else:
        raise HTTPException(status_code=404, detail="Order not found")


@app.get("/orders/", response_model=List[schemas.Order])
async def read_item():
    query = await mongoDB.orders.find().to_list(None)
    return query
