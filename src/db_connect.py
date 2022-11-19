import cx_Oracle
from sqlalchemy import types, create_engine
import pandas as pd
import downloadDB


def connect_to_oracle_pandas(name,password):
    return create_engine('oracle://{}:{}@gort.fit.vutbr.cz:1521/orclpdb'.format(name,password))

def connect_to_oracle_cursor(name,password):
    conn = cx_Oracle.connect('{}/{}@gort.fit.vutbr.cz:1521/orclpdb'.format(name,password))
    return conn.cursor()

if __name__ == '__main__':
    conn = connect_to_oracle_pandas('xlogin','password')
    
    print(conn)
    df = pd.read_csv('pdb_dataset.csv')
    df.to_sql('products', conn, if_exists='replace')
    
    #RawData= pd.read_sql_query("select * from products", conn)
    #RawData.head()