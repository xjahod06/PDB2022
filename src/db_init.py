import models
from db_connect import *
import configparser

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.conf')
    engine = connect_to_oracle(config['oracle_sql']['name'],config['oracle_sql']['password'])
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)