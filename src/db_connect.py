import cx_Oracle
from sqlalchemy import types, create_engine
import pandas as pd
import downloadDB
import configparser
from pymongo import MongoClient
import json

def connect_to_oracle(name,password):
    dsn = cx_Oracle.makedsn(
        'gort.fit.vutbr.cz', 
        1521,
        service_name='orclpdb'
    )
    return create_engine(f"oracle+cx_oracle://{name}:{password}@{dsn}")

def connect_to_oracle_cursor(name,password):
    conn = cx_Oracle.connect('{}/{}@gort.fit.vutbr.cz:1521/orclpdb'.format(name,password))
    return conn.cursor()

def df_to_sql_db(engine,df):
    with engine.connect() as connection:
        df.to_sql('products', connection, if_exists='replace')

def get_oracle_data(engine,show=True):
    with engine.connect() as connection:
        rawData = pd.read_sql_query("SELECT * FROM products", connection)
        print(rawData.head()) if show == True else None
        return rawData

def connect_to_mongo(name,password):
    return MongoClient(config['mongo_db']['uri'].format(name,password))['pdb']

def df_to_mongo(db,df):
    db.products.insert_many(df.to_dict('records'), ordered=False)
    
def get_mongo_data(db,show=True):
    df = pd.DataFrame(list(mongoDb.myCollection.find()))
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
    
    df_to_mongo(mongoDb,df)
    get_mongo_data(mongoDb)