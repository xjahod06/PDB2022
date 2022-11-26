from typing import List, Union
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import crud, models, schemas

from datetime import datetime
from db_connect import *
import configparser
from pymongo import MongoClient


config = configparser.ConfigParser()
config.read('config.conf')
mongoDB = connect_to_mongo(config['mongo_db']['name'],config['mongo_db']['password'])

engine = connect_to_oracle(config['oracle_sql']['name'],config['oracle_sql']['password'])
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/oracle/products/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = crud.create_product(db=db, product=product)
    if db_product is None:
        raise HTTPException(status_code=400, detail="this product is already in DB")
    return db_product

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
    with connect_to_oracle_cursor(config['oracle_sql']['name'],config['oracle_sql']['password']) as connection:
        return insert_product(connection,product)
    return 'error in oracle connection'

@app.get("/products/", response_model=List[schemas.Product])
def read_item():
    query = mongoDB.products.find()
    return [q for q in query]

@app.get("/products/{product_id}", response_model=schemas.Product)
def read_item(product_id: int):
    query = mongoDB.products.find({"_id" : product_id})
    return query[0]

@app.put("/products/{product_id}", response_model=schemas.Product)
def read_item(product_id: int, product: schemas.Product):
    pass
    return product

@app.delete("/products/{product_id}", status_code=200)
def read_item(product_id: int):
    result = mongoDB.products.delete_one({"_id" : product_id})
    if result.deleted_count != 1:
        raise HTTPException(status_code=404, detail="Item not found")
    else:
        return

@app.get("/price/", response_model=List[schemas.Product])
def read_item(price: float):
    query = mongoDB.products.find({"price" : price})
    return [q for q in query]

@app.get("/priceRange/", response_model=List[schemas.Product])
def read_item(gt: Union[float,None] = 0, lt: Union[float,None] = None):
    if lt:
        query = mongoDB.products.find({"price" : {"$gt": gt, "$lt": lt}})
    else:
        query = mongoDB.products.find({"price" : {"$gt": gt}})
    return [q for q in query]

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

@app.get("/inStockRange/", response_model=List[schemas.Product])
def read_item(gt: Union[int,None] = 0, lt: Union[int,None] = None):
    if lt:
        query = mongoDB.products.find({"in_stock" : {"$gt": gt, "$lt": lt}})
    else:
        query = mongoDB.products.find({"in_stock" : {"$gt": gt}})
    return [q for q in query]

@app.get("/category/{category}")
def read_item(category: str):
    pass
    #TODO categorie jsou v sku tak to rozkličovat a vratit
    return None

@app.get("/brand/{brand}", response_model=schemas.Product)
def read_item(brand: str):
    query = mongoDB.products.find({"brand" : brand})
    return query[0]

@app.get("/inDescription/{key_word}", response_model=List[schemas.Product])
def read_item(key_word: str):
    query = mongoDB.products.find({"description" : {"$regex" : key_word}})
    return [q for q in query]