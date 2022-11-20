import cx_Oracle
from sqlalchemy import types, create_engine
import pandas as pd
import downloadDB
import configparser
from pymongo import MongoClient
import json
from time import time

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

def insert_product(connection,title,images,description,sku,gtin13,brand,price,currency,in_stock):
    sql = ('insert into products(title,images,description,sku,gtin13,brand,price,currency,in_stock,added_at) '
        'values(:title,:images,:description,:sku,:gtin13,:brand,:price,:currency,:in_stock,:added_at)')
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, [title,images,description,sku,gtin13,brand,price,currency,in_stock,time()])
            return connection.commit()
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
    df = pd.read_csv('pdb_dataset.csv')
    
    df_to_sql_db(engine,df) 
    get_oracle_data(engine)

    mongoDb = connect_to_mongo(config['mongo_db']['name'],config['mongo_db']['password'])
    
    #removed previously inserted data
    mongoDb.products.delete_many({})
    
    df_to_mongo(mongoDb,df)
    get_mongo_data(mongoDb)
    
    #query = mongoDb.products.find({"product_id" : 313486617})
    #print(query[0])
    #for q in query:
    #    print(q)