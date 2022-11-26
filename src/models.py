from sqlalchemy import Column, Integer, Float, String, DateTime, Identity, Text, UnicodeText #ForeignKey
from datetime import datetime
#from sqlalchemy.orm import relationship

from db_connect import Base

class Product(Base):
    __tablename__ = "products"
    
    _id = Column(Integer, Identity(start=1), primary_key=True,) #index=True,
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