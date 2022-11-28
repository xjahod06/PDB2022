import models
from fastapi import Depends
import pandas as pd
from db_connect import *
import configparser
from sqlalchemy.orm import Session
from datetime import datetime
import logging

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def create_product(product: pd.DataFrame,db: Session = Depends(get_db)):
    db_product = models.Product(**product)
    db_gen = get_db()
    db = next(db_gen)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    config = configparser.ConfigParser()
    config.read('config.conf')
    engine = connect_to_oracle(config['oracle_sql']['name'],config['oracle_sql']['password'])
    logging.debug("dropped database")
    models.Base.metadata.drop_all(bind=engine)
    logging.debug("created database")
    models.Base.metadata.create_all(bind=engine)
    
    logging.debug("loaded df")
    df = pd.read_csv('pdb_dataset.csv')
    sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    logging.debug("started loading df to db")
    percentCount = 0
    for index,row in df.iterrows():
        row = row.to_dict()
        row['added_at'] = datetime.strptime(row['added_at'],"%Y-%m-%d %H:%M:%S")
        create_product(row)
        if ((index+1) % int(len(df)/10)) == 0:
            percentCount += 1
            logging.debug("loaded {} %...".format(percentCount*10))
            
    mongoDb = connect_to_mongo(config['mongo_db']['name'],config['mongo_db']['password'])
    logging.debug("connected to mongoDB")
    
    #removed previously inserted data
    mongoDb.products.delete_many({})
    logging.debug("deleted previous data")
    
    logging.debug("uploading to mongoDB")
    df_to_mongo(mongoDb,df)