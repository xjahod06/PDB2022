from sqlalchemy.orm import Session
import models
import schemas
from datetime import datetime

def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product._id == product_id).first()

def get_products(db: Session ):             #, skip: int = 0, limit: int = 100):
    return db.query(models.Product).all()   #.offset(skip).limit(limit).all()


def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product