from sqlalchemy import types, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import cx_Oracle
import pandas as pd
import downloadDB
import configparser
from pymongo import MongoClient
import json
from time import time

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
    with engine.connect() as connection:
        df.to_sql('products', connection, if_exists='replace')

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
    config = configparser.ConfigParser()
    config.read('config.conf')
    name = config['oracle_sql']['name']
    password = config['oracle_sql']['password']
    
    engine = connect_to_oracle(name, password)
    sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    df = pd.read_csv('pdb_dataset.csv')
    
    df_to_sql_db(engine,df) 
    get_oracle_data(engine)

    mongoDb = connect_to_mongo(config['mongo_db']['name'],config['mongo_db']['password'])
    
    #removed previously inserted data
    mongoDb.products.delete_many({})
    
    df_to_mongo(mongoDb,df)
    get_mongo_data(mongoDb)