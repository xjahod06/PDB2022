from sqlalchemy import types, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Integer, String, DateTime, Text, UnicodeText, Float
from datetime import datetime


import cx_Oracle
import pandas as pd
import configparser
from pymongo import MongoClient
from time import time
import logging

Base = declarative_base()

def connect_to_oracle(name,password):
    dsn = cx_Oracle.makedsn(
        'gort.fit.vutbr.cz', 
        1521,
        service_name='orclpdb'
    )
    return create_engine(f"oracle+cx_oracle://{name}:{password}@{dsn}")

def connect_to_oracle_cursor(name,password):
    return cx_Oracle.connect('{}/{}@gort.fit.vutbr.cz:1521/orclpdb'.format(name,password))

def df_to_sql_db(engine,df):
    df_schema = {
        "_id" : Integer,
        "title" : String(256),
        "images" : Text,
        "description" : UnicodeText,
        "sku" : Integer,
        "gtin13" : Integer,
        "brand" : String(50),
        "price" : Float,
        "currency" : String(6),
        "in_stock" : Integer,
        #"added_at" : DateTime,
    }
    with engine.connect() as connection:
        df.to_sql('products', connection, if_exists='append', dtype=df_schema,index=False)

def get_oracle_data(engine,show=True):
    with engine.connect() as connection:
        rawData = pd.read_sql_query("SELECT * FROM products", connection)
        print(rawData.head()) if show == True else None
        return rawData

def insert_product(connection,product):
    sql = ('insert into products(title,images,description,sku,gtin13,brand,price,currency,in_stock,added_at) '
        'values(:title,:images,:description,:sku,:gtin13,:brand,:price,:currency,:in_stock,:added_at)'
        'returning \"_id\" into :python_var')
    try:
        with connection.cursor() as cursor:
            newest_id_wrapper = cursor.var(cx_Oracle.NUMBER)
            cursor.execute(sql, [
                product.title,
                product.images,
                product.description,
                product.sku,
                product.gtin13,
                product.brand,
                product.price,
                product.currency,
                product.in_stock,
                time(),
                newest_id_wrapper
            ])
            connection.commit()
            return newest_id_wrapper.getvalue()
    except cx_Oracle.Error as error:
        return "some of cx_Oracle.Error" + str(error)

def connect_to_mongo(name,password):
    return MongoClient("mongodb://{}:{}@localhost:28017/pdb?authSource=admin".format(name,password))['pdb']

def df_to_mongo(db,df):
    db.products.insert_many(df.to_dict('records'), ordered=False)
    
def get_mongo_data(db,show=True):
    df = pd.DataFrame(list(mongoDb.products.find()))
    print(df.head()) if show == True else None
    return df

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    config = configparser.ConfigParser()
    config.read('config.conf')
    name = config['oracle_sql']['name']
    password = config['oracle_sql']['password']
    
    engine = connect_to_oracle(name, password)
    logging.debug("started oracel engine")
    
    df = pd.read_csv('pdb_dataset.csv')
    logging.debug("loaded dataframe")
    logging.debug("uploading df to oracle SQL")
    df_to_sql_db(engine,df) 
    logging.debug("upload successfull")
    get_oracle_data(engine,show=False)

    mongoDb = connect_to_mongo(config['mongo_db']['name'],config['mongo_db']['password'])
    logging.debug("connected to mongoDB")
    
    #removed previously inserted data
    mongoDb.products.delete_many({})
    logging.debug("deleted previous data")
    
    logging.debug("uploading to mongoDB")
    df_to_mongo(mongoDb,df)
    logging.debug("upload succesfull")
    get_mongo_data(mongoDb,show=False)