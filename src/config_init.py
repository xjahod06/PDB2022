import configparser
import sys

try:
    sql_name = sys.argv[1]
    sql_pass = sys.argv[2]
    config = configparser.ConfigParser()
    config.read('config_template.conf')

    config.set('oracle_sql', 'name', sql_name)
    config.set('oracle_sql', 'password', sql_pass)

    with open(r'config.conf','w') as configureation:
        config.write(configureation)
except TypeError as e:
    print (e)
    exit