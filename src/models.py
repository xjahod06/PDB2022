from sqlalchemy import Column, Integer, String, DateTime,Identity #Boolean, ForeignKey
from datetime import datetime
#from sqlalchemy.orm import relationship

from db_connect import Base

class Product(Base):
    __tablename__ = "products"
    
    _id = Column(Integer, Identity(start=1), primary_key=True,) #index=True,
    title = Column(String(50))
    images = Column(String(50), default=None)
    description = Column(String(50), default=None)
    sku = Column(Integer)
    gtin13 = Column(Integer)
    brand = Column(String(50))
    price = Column(Integer)
    currency = Column(String(50))
    in_stock = Column(Integer)
    added_at = Column(DateTime, default=datetime.utcnow)