from typing import List, Union, Tuple
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import crud
import schemas

from db_connect import *
import configparser


config = configparser.ConfigParser()
config.read('config.conf')
mongoDBSync = connect_to_mongo(
    config['mongo_db']['name'], config['mongo_db']['password'])

engine = connect_to_oracle(
    config['oracle_sql']['name'], config['oracle_sql']['password'])
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()


def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_product_mongo(product: dict):
    return mongoDBSync.products.insert_one(product)


def create_order_mongo(order: dict):
    return mongoDBSync.orders.insert_one(order)


@app.post("/products/", response_model=schemas.Product)
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
    
@app.post("/order/", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate,product_ids : List[int],amounts : List[int], db: Session = Depends(get_db)):
    db_order = crud.create_order(db=db, order=order,product_ids=product_ids,amounts=amounts)
    if db_order is None:
        raise HTTPException(
            status_code=400, detail="db si broken :) ")
    else:
        res = (create_order_mongo(db_order.as_dict()))
        if (res.inserted_id != db_order._id):
            raise HTTPException(
                status_code=500, detail="sync between mongo and oracle failed")
        return db_order

def update_order_mongo(order: dict):
    filter = {'_id': order["_id"]}
    new = {"$set": order}
    return mongoDBSync.orders.update_one(filter, new)

@app.put("/order/{order_id}", response_model=schemas.Order)
def update_order(order_id: int, order: schemas.OrderUpdate,db: Session = Depends(get_db)):
    db_order = crud.update_order(db,order_id,order)
    if db_order is None:
        raise HTTPException(
            status_code=400, detail="this order does not exist")
    else:
        result = update_order_mongo(db_order.as_dict())
        if (result.modified_count != 1):
            raise HTTPException(
                status_code=500, detail="Update to mongo failed")
    return db_order

@app.put("/order/{order_id}/addProduct/{product_id}", response_model=schemas.Order)
def add_product_to_order(order_id: int, product_id: int,amount: int = 1,db: Session = Depends(get_db)):
    db_order = crud.add_product_to_order(db,order_id,product_id,amount)
    if db_order is None:
        raise HTTPException(
            status_code=400, detail="this product or order does not exist")
    else:
        return db_order

def update_product_mongo(product: dict):
    filter = {'_id': product["_id"]}
    new = {"$set": product}
    return mongoDBSync.products.update_one(filter, new)


@app.put("/products/{product_id}", response_model=schemas.Product)
def update_product(product_id: int, product: schemas.ProductUpdate, db: Session = Depends(get_db)):
    db_product = crud.update_product(db, product_id, product)
    if db_product is None:
        raise HTTPException(
            status_code=400, detail="this product does not exist")
    else:
        result = update_product_mongo(db_product.as_dict())
        if (result.modified_count != 1):
            raise HTTPException(
                status_code=500, detail="Update to mongo failed")
    return db_product


@app.put("/products/buy/{product_id}", response_model=schemas.Product)
def buy_product(product_id: int, count: int,order_id: Union[int,None] = None, order: Union[schemas.OrderCreate,None] = None, db: Session = Depends(get_db)):
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

    if order_id is not None:
        db_order = crud.get_order(db,order_id)
        if db_order is None:
            raise HTTPException(status_code=400, detail=f"Order doesn't exist")      
    
    # update in stock status
    db_product.in_stock = db_product.in_stock - count
    updated_product = crud.update_product(db, product_id, db_product)
    if updated_product is None:
        raise HTTPException(status_code=400, detail="Update to oracle failed")
    else:
        #creating an order
        if order_id is None:
            db_order = create_order(order,[product_id],[count],db)
        else:
            print("add_to_db")
            db_order = add_product_to_order(order_id,product_id,count,db)
        
        result = update_product_mongo(updated_product.as_dict())
        if (result.modified_count != 1):
            raise HTTPException(
                status_code=500, detail="Update to mongo failed")
    return updated_product


@app.get("/products/{product_id}", response_model=schemas.Product)
def read_product_oracle(product_id: int, db: Session = Depends(get_db)):
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


@app.get("/products/", response_model=List[schemas.Product])
def read_all_products_oracle(db: Session = Depends(get_db)):
    products = crud.get_products(db)
    return products