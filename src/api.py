from typing import List, Union
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import crud
import models
import schemas

from datetime import datetime
from db_connect import *
import configparser

config = configparser.ConfigParser()
config.read('config.conf')
mongoDB = async_connect_to_mongo(
    config['mongo_db']['name'], config['mongo_db']['password'])
mongoDBSync = connect_to_mongo(
    config['mongo_db']['name'], config['mongo_db']['password'])

engine = connect_to_oracle(
    config['oracle_sql']['name'], config['oracle_sql']['password'])
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency


def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_product_mongo(product: dict):
    return mongoDBSync.products.insert_one(product)


@app.post("/oracle/products/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = crud.create_product(db=db, product=product)
    if db_product is None:
        raise HTTPException(
            status_code=400, detail="this product is already in DB")
    else:
        res = (create_product_mongo(db_product.as_dict()))
        if (res.inserted_id != db_product._id):
            raise HTTPException(
                status_code=500, detail="sync between mongo and oracle failed")
        return db_product
    
@app.post("/oracle/order/", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate,product_id : int, db: Session = Depends(get_db)):
    db_order = crud.create_order(db=db, order=order,product_id=product_id)
    if db_order is None:
        raise HTTPException(
            status_code=400, detail="db si broken :) ")
    else:
        # res = (create_product_mongo(db_product.as_dict()))
        # if (res.inserted_id != db_product._id):
        #     raise HTTPException(
        #         status_code=500, detail="sync between mongo and oracle failed")
        return db_order


def update_product_mongo(product: dict):
    filter = {'_id': product["_id"]}
    print(filter)
    new = {"$set": product}
    print(new)
    return mongoDBSync.products.update_one(filter, new)


@app.put("/products/{product_id}", response_model=schemas.Product)
def read_item(product_id: int, product: schemas.ProductUpdate, db: Session = Depends(get_db)):
    db_product = crud.update_product(db, product_id, product)
    if db_product is None:
        raise HTTPException(
            status_code=400, detail="this product is already in DB")
    else:
        update_product_mongo(db_product.as_dict())
        # if (res.upserted_id != db_product._id):
        #    raise HTTPException(status_code=500, detail="sync between mongo and oracle failed mongoID - {} oracle - {}".format(res.upserted_id, db_product._id))
    return db_product


@app.put("/products/buy/{product_id}", response_model=schemas.Product)
def read_item(product_id: int, count: int, db: Session = Depends(get_db)):
    """Endpoint that is called when customer wants to buy an item"""
    # check that at least one product was requested
    if count <= 0:
        raise HTTPException(status_code=400,
                            detail=f"{count} is incorrect number of products to buy")

    # check that requested product exists
    db_product = crud.get_product(db, product_id)
    if db_product is None:
        raise HTTPException(status_code=400, detail=f"Product doesn't exist")

    # check that enough products are in stock
    if db_product.in_stock < count:
        error_msg = f"""Not enough products in store. Requested: {count}, In stock: {db_product.in_stock}"""
        raise HTTPException(status_code=400, detail=error_msg)

    # update in stock status
    db_product.in_stock = db_product.in_stock - count
    updated_product = crud.update_product(db, product_id, db_product)
    if updated_product is None:
        raise HTTPException(status_code=400, detail="Update to oracle failed")
    else:
        result = update_product_mongo(updated_product.as_dict())
        print(result.upserted_id)
        if (result.modified_count != 1):
            raise HTTPException(
                status_code=500, detail="Update to mongo failed")
    return updated_product


@app.get("/oracle/products/{product_id}", response_model=schemas.Product)
def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


@app.get("/oracle/products/", response_model=List[schemas.Product])
def read_products(db: Session = Depends(get_db)):
    products = crud.get_products(db)
    return products


@app.post("/products/")
def read_item(product: schemas.Product):
    with connect_to_oracle_cursor(config['oracle_sql']['name'], config['oracle_sql']['password']) as connection:
        return insert_product(connection, product)
    return 'error in oracle connection'


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


@app.get("/inDescription/{key_word}", response_model=List[schemas.Product])
async def read_item(key_word: str):
    query = await mongoDB.products.find({"description": {"$regex": key_word}}).to_list(None)
    return query
