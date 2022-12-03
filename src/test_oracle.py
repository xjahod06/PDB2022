import configparser
from datetime import datetime
import json

from fastapi.testclient import TestClient
import pytest
import sqlalchemy as db

from api_oracle import app
from db_connect import connect_to_oracle
import models
import schemas


config = configparser.ConfigParser()
config.read('config.conf')
name = config['oracle_sql']['name']
password = config['oracle_sql']['password']
engine = connect_to_oracle(name, password)

client = TestClient(app)

test_product = {
    "title": "Test product",
    "images": "https://test.product.url",
    "description": "This is a description of an abstract test product",
    "sku": 1111111111,
    "gtin13": 111111111111,
    "brand": "Test brand",
    "price": 69,
    "currency": "USD",
    "in_stock": 2,
}

test_order = {
    "status": "Test order status",
    "price": 69,
    "user_information": "test user info",
    "transport_information": "test transport info",
    "query": "test query",
}


# setup and teardown
@pytest.fixture
def create_and_delete_test_product():
    connection = engine.connect()
    products_table = db.Table('products', db.MetaData(), autoload=True, autoload_with=engine)
    query = db.insert(products_table).values(**test_product) 
    connection.execute(query)
    yield query
    query = db.delete(products_table).where(products_table.columns.title == 'Test product')
    connection.execute(query)


@pytest.fixture
def delete_test_product():
    yield None
    connection = engine.connect()
    products_table = db.Table('products', db.MetaData(), autoload=True, autoload_with=engine)
    query = db.delete(products_table).where(products_table.columns.title == 'Test product')
    connection.execute(query)


@pytest.fixture
def delete_test_order():
    yield None
    connection = engine.connect()
    order_product_table = db.Table('order_product', db.MetaData(), autoload=True, autoload_with=engine)
    products_table = db.Table('products', db.MetaData(), autoload=True, autoload_with=engine)
    orders_table = db.Table('orders', db.MetaData(), autoload=True, autoload_with=engine)

    query = db.delete(products_table).where(products_table.columns.title == 'Test product')
    result = connection.execute(query).fetchall()[0]

    query = db.delete(order_product_table).where(order_product_table.columns.order_id == result[0])
    connection.execute(query)

    query = db.delete(orders_table).where(orders_table.columns.query == 'test query')
    connection.execute(query)


@pytest.fixture
def fully_delete_order():
    connection = engine.connect()
    products_table = db.Table('products', db.MetaData(), autoload=True, autoload_with=engine)
    query = db.insert(products_table).values(**test_product) 
    connection.execute(query)
    yield query

    order_product_table = db.Table('order_product', db.MetaData(), autoload=True, autoload_with=engine)
    orders_table = db.Table('orders', db.MetaData(), autoload=True, autoload_with=engine)

    query = db.select(orders_table).where(orders_table.columns.query == 'test query')
    result = connection.execute(query).fetchall()[0]

    query = db.delete(order_product_table).where(order_product_table.columns.order_id == result[0])
    connection.execute(query)

    query = db.delete(orders_table).where(orders_table.columns.query == 'test query')
    connection.execute(query)

    query = db.delete(products_table).where(products_table.columns.title == 'Test product')
    connection.execute(query)



# ============================TESTS==================================
def test_get_products(create_and_delete_test_product):
    connection = engine.connect()
    products_table = db.Table('products', db.MetaData(), autoload=True, autoload_with=engine)
    query = db.select([products_table]).where(products_table.columns.title == 'Test product')
    result = connection.execute(query).fetchall()

    query = db.select([products_table])
    num_of_products = len(connection.execute(query).fetchall())
    response = client.get("/products")

    assert response.status_code == 200
    assert len(response.json()) == num_of_products
    assert test_product['title'] in [prod['title'] for prod in response.json()]


def test_get_product(create_and_delete_test_product):
    connection = engine.connect()
    products_table = db.Table('products', db.MetaData(), autoload=True, autoload_with=engine)
    query = db.select([products_table]).where(products_table.columns.title == 'Test product')
    result = connection.execute(query).fetchall()[0]
    response = client.get(f"/products/{result[0]}")

    assert response.status_code == 200
    for key in test_product:
        if key in ['_id', 'added_at']:
            continue
        assert response.json()[key] == test_product[key]


def test_post_products(delete_test_product):
    response = client.post(f"/products/", json=test_product)
    assert response.status_code == 200

    connection = engine.connect()
    products_table = db.Table('products', db.MetaData(), autoload=True, autoload_with=engine)
    query = db.select([products_table]).where(products_table.columns.title == 'Test product')
    result = connection.execute(query).fetchall()[0]

    for key, val in test_product.items():
        if key in ['_id', 'added_at']:
            continue
        assert val == test_product[key]


def test_post_orders(fully_delete_order):
    connection = engine.connect()
    products_table = db.Table('products', db.MetaData(), autoload=True, autoload_with=engine)
    query = db.select([products_table]).where(products_table.columns.title == 'Test product')
    test_product = connection.execute(query).fetchall()[0]

    order_json = {
        "order": test_order,
        "product_ids": [
            test_product["_id"]
        ],
        "amounts": [
            1
        ]
    }
    response = client.post(f"/order/", json=order_json)
    assert response.status_code == 200

    connection = engine.connect()
    orders_table = db.Table('orders', db.MetaData(), autoload=True, autoload_with=engine)
    query = db.select([orders_table]).where(orders_table.columns.query == 'test query')
    result = connection.execute(query).fetchall()[0]

    for key, val in test_order.items():
        if key in ['_id', 'added_at']:
            continue
        assert val == test_order[key]


def test_put_product(create_and_delete_test_product):
    connection = engine.connect()
    products_table = db.Table('products', db.MetaData(), autoload=True, autoload_with=engine)
    query = db.select([products_table]).where(products_table.columns.title == 'Test product')
    db_product = connection.execute(query).fetchall()[0]
    
    test_product['title'] = 'Test product EDITED'
    response = client.put(f"/products/{db_product[0]}", json=test_product)
    assert response.status_code == 200

    query = db.select([products_table]).where(products_table.columns.title == 'Test product EDITED')
    new_db_product = connection.execute(query).fetchall()[0]

    for original, new in zip(db_product[2:], new_db_product[2:]):
        assert original == new


def test_buy_product(create_and_delete_test_product):
    pass
