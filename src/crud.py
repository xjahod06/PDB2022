from sqlalchemy.orm import Session
import models
import schemas
from datetime import datetime
from typing import List


def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product._id == product_id).first()


def get_products(db: Session):  # , skip: int = 0, limit: int = 100):
    return db.query(models.Product).all()  # .offset(skip).limit(limit).all()


def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, product_id: int, product: schemas.Product):
    updated_product = db.query(models.Product).filter(
        models.Product._id == product_id).first()
    updated_product.update_values(product.as_dict())
    db.commit()
    return updated_product


def create_order(db: Session, order: schemas.OrderCreate, product_ids: List[int]):
    db_order = models.Order(**order.dict())

    for product_id in product_ids:
        db_product = db.query(models.Product).filter(models.Product._id == product_id).first()
        db_product_order = models.ProductOrder(amount=1)
        db_product_order.product = db_product
        db_order.products.append(db_product_order)
    db.add(db_order)

    db.commit()
    db.refresh(db_order)
    return db_order

