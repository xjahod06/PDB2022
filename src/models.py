from sqlalchemy import Column, Integer, Float, String, DateTime, Identity, Text, UnicodeText, ForeignKey, Table
from datetime import datetime
from sqlalchemy.orm import relationship

from db_connect import Base

class ProductOrder(Base):
    __tablename__ = "order_product"
    
    product_id = Column(ForeignKey("products._id"), primary_key = True)
    order_id = Column(ForeignKey("orders._id"), primary_key = True)
    amount = Column(Integer)
    product = relationship("Product", back_populates="orders")
    order = relationship("Order", back_populates="products")

class Product(Base):
    __tablename__ = "products"
    
    _id = Column(Integer, Identity(start=1), primary_key=True)
    title = Column(String(256))
    images = Column(Text, default=None)
    description = Column(UnicodeText, default=None)
    sku = Column(Integer)
    gtin13 = Column(Integer)
    brand = Column(String(50))
    price = Column(Float)
    currency = Column(String(6))
    in_stock = Column(Integer)
    added_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    
    orders = relationship("ProductOrder", back_populates="product")
    
    def as_dict(self):
           return {c.name: getattr(self, c.name) for c in self.__table__.columns}
   
    def update_values(self,newdata):
        self.title = newdata["title"] if newdata["title"] is not None else self.title
        self.images = newdata["images"] if newdata["images"] is not None else self.images
        self.description = newdata["description"] if newdata["description"] is not None else self.description
        self.sku = newdata["sku"] if newdata["sku"] is not None else self.sku
        self.gtin13 = newdata["gtin13"] if newdata["gtin13"] is not None else self.gtin13
        self.brand = newdata["brand"] if newdata["brand"] is not None else self.brand
        self.price = newdata["price"] if newdata["price"] is not None else self.price
        self.currency = newdata["currency"] if newdata["currency"] is not None else self.currency
        self.in_stock = newdata["in_stock"] if newdata["in_stock"] is not None else self.in_stock
        


class Order(Base):
    __tablename__ = "orders"
    
    _id = Column(Integer, Identity(start=1), primary_key=True)
    price = Column(Float)
    user_information = Column(UnicodeText, default=None)
    transport_information = Column(UnicodeText, default=None)
    status = Column(String(25))
    query = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    
    products = relationship("ProductOrder", back_populates="order")
