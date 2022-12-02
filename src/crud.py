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
    updated_product = get_product(db,product_id)
    if updated_product is None:
        return None
    if type(product) is schemas.Product:
        updated_product.update_values(product.dict())
    else:
        updated_product.update_values(product.as_dict())
    db.commit()
    return updated_product


def create_order(db: Session, order: schemas.OrderCreate, product_ids: List[int], amounts: List[int]):
    db_order = models.Order(**order.dict())
    price = 0
    for product_id,amount in zip(product_ids,amounts):
        db_product = db.query(models.Product).filter(models.Product._id == product_id).first()
        price += (db_product.price*amount)
        db_product_order = models.ProductOrder(amount=amount)
        db_product_order.product = db_product
        db_order.products.append(db_product_order)
    db_order.price = price
    db_order.status = "created"
    db.add(db_order)

    db.commit()
    db.refresh(db_order)
    return db_order

def update_order(db:Session,order_id: int, order: schemas.Order):
    update_order = get_order(db,order_id)
    if update_order is None:
        return None
    if type(order) is schemas.Order:
        update_order.update_values(order.dict())
    else:
        update_order.update_values(order.as_dict())
    db.commit()
    return update_order

def add_product_to_order(db:Session,order_id: int,product_id: int,amount: int = 1):
    db_order = get_order(db,order_id)
    if db_order is None:
        return None
    db_product = get_product(db,product_id)
    if db_product is None:
        return None
    db_product_order = models.ProductOrder(amount=amount)
    db_product_order.product = db_product
    db_order.products.append(db_product_order)
    db_order.price += (db_product.price*amount)
    db.commit()
    return db_order

def get_order(db: Session, order_id: int):
    return db.query(models.Order).filter(models.Order._id == order_id).first()