from sqlalchemy import Column, Integer, String, DATETIME #Boolean, ForeignKey
#from sqlalchemy.orm import relationship

from db_connect import Base

class Product(Base):
    __tablename__ = "products"
    
    _id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    images = Column(String, default=None)
    description = Column(String, default=None)
    sku = Column(Integer)
    gtin13 = Column(Integer)
    brand = Column(String)
    price = Column(Integer)
    currency = Column(String)
    in_stock = Column(Integer)
    added_at = Column(DATETIME)