import cx_Oracle
from sqlalchemy import types, create_engine
import pandas as pd
import downloadDB
import configparser


def connect_to_oracle_pandas(name,password):
    dsn = cx_Oracle.makedsn(
        'gort.fit.vutbr.cz', 
        1521,
        service_name='orclpdb'
    )
    return create_engine(f"oracle+cx_oracle://{name}:{password}@{dsn}")

def connect_to_oracle_cursor(name,password):
    conn = cx_Oracle.connect('{}/{}@gort.fit.vutbr.cz:1521/orclpdb'.format(name,password))
    return conn.cursor()

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.conf')
    name = config['oracle_sql']['name']
    password = config['oracle_sql']['password']
    
    engine = connect_to_oracle_pandas(name, password)
    df = pd.read_csv('pdb_dataset.csv')

    with engine.connect() as connection:
        df.to_sql('products', connection, if_exists='replace')

    with engine.connect() as connection:
        rawData = pd.read_sql_query("SELECT * FROM products", connection)
        print(rawData.head())