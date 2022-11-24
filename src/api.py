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
    return crud.create_product(db=db, product=product)

@app.get("/oracle/products/{product_id}", response_model=schemas.Product)
def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

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