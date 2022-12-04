import configparser
from datetime import datetime
import json

from fastapi.testclient import TestClient
import pytest
import sqlalchemy as db

from api_oracle import app
from db_connect import connect_to_oracle, connect_to_mongo
from test_mongo import create_and_delete_test_product, create_and_delete_test_order


config = configparser.ConfigParser()
config.read('config.conf')
name = config['oracle_sql']['name']
password = config['oracle_sql']['password']
engine = connect_to_oracle(name, password)
mongoDB = connect_to_mongo(
    config['mongo_db']['name'], config['mongo_db']['password'])

client = TestClient(app)

test_product = {
    "_id": 69696969,
    "title": "Test product",
    "images": "https://test.product.url",
    "description": "This is a description of an abstract test product",
    "sku": 1111111111,
    "gtin13": 111111111111,
    "brand": "Test brand",
    "price": 69,
    "currency": "USD",
    "in_stock": 4,
    "added_at": datetime.utcnow()
}

test_order = {
    "_id": 420420420,
    "status": "created",
    "price": 69,
    "user_information": "test user info",
    "transport_information": "test transport info",
    "query": "test query",
}


# setup and teardown
@pytest.fixture
def create_and_delete_test_product_oracle():
    connection = engine.connect()
    products_table = db.Table(
        'products', db.MetaData(), autoload=True, autoload_with=engine)
    query = db.insert(products_table).values(**test_product)
    connection.execute(query)
    yield query
    query = db.delete(products_table).where(
        products_table.columns._id == test_product['_id'])
    connection.execute(query)
    mongoDB.products.delete_many({'title': 'Test product'})


@pytest.fixture
def delete_test_product():
    yield None
    connection = engine.connect()
    products_table = db.Table(
        'products', db.MetaData(), autoload=True, autoload_with=engine)
    query = db.delete(products_table).where(
        products_table.columns.title == 'Test product')
    connection.execute(query)
    mongoDB.products.delete_many({'title': 'Test product'})


@pytest.fixture
def delete_test_order():
    yield None
    connection = engine.connect()
    order_product_table = db.Table(
        'order_product', db.MetaData(), autoload=True, autoload_with=engine)
    products_table = db.Table(
        'products', db.MetaData(), autoload=True, autoload_with=engine)
    orders_table = db.Table('orders', db.MetaData(),
                            autoload=True, autoload_with=engine)

    query = db.delete(products_table).where(
        products_table.columns.title == 'Test product')
    result = connection.execute(query).fetchall()[0]

    query = db.delete(order_product_table).where(
        order_product_table.columns.order_id == result[0])
    connection.execute(query)

    query = db.delete(orders_table).where(
        orders_table.columns.query == 'test query')
    connection.execute(query)
    mongoDB.products.delete_many({'title': 'Test product'})
    mongoDB.orders.delete_many({'user_information': 'test user info'})


@pytest.fixture
def create_product_and_fully_delete_order():
    connection = engine.connect()
    products_table = db.Table(
        'products', db.MetaData(), autoload=True, autoload_with=engine)
    query = db.insert(products_table).values(**test_product)
    connection.execute(query)
    yield query

    order_product_table = db.Table(
        'order_product', db.MetaData(), autoload=True, autoload_with=engine)
    orders_table = db.Table('orders', db.MetaData(),
                            autoload=True, autoload_with=engine)

    query = db.select(orders_table).where(
        orders_table.columns.query == 'test query')
    result = connection.execute(query).fetchall()[0]

    query = db.delete(order_product_table).where(
        order_product_table.columns.order_id == result[0])
    connection.execute(query)

    query = db.delete(orders_table).where(
        orders_table.columns.query == 'test query')
    connection.execute(query)

    query = db.delete(products_table).where(
        products_table.columns.title == 'Test product')
    connection.execute(query)
    mongoDB.products.delete_many({'title': 'Test product'})
    mongoDB.orders.delete_many({'user_information': 'test user info'})


@pytest.fixture
def create_and_delete_order_product(create_and_delete_test_product, create_and_delete_test_order):
    # setup
    connection = engine.connect()
    products_table = db.Table(
        'products', db.MetaData(), autoload=True, autoload_with=engine)
    query = db.insert(products_table).values(**test_product)
    connection.execute(query)
    orders_table = db.Table('orders', db.MetaData(),
                            autoload=True, autoload_with=engine)
    order_product_table = db.Table(
        'order_product', db.MetaData(), autoload=True, autoload_with=engine)
    query = db.insert(orders_table).values(**test_order)
    db_order = connection.execute(query)
    yield db_order

    # cleanup
    query = db.delete(order_product_table).where(
        order_product_table.columns.order_id == test_order['_id'])
    connection.execute(query)

    query = db.delete(orders_table).where(
        orders_table.columns.query == 'test query')
    connection.execute(query)

    query = db.delete(products_table).where(
        products_table.columns.title == 'Test product')
    connection.execute(query)
    mongoDB.products.delete_many({'title': 'Test product'})
    mongoDB.orders.delete_many({'user_information': 'test user info'})


# ============================TESTS==================================
def test_get_products(create_and_delete_test_product_oracle):
    connection = engine.connect()
    products_table = db.Table(
        'products', db.MetaData(), autoload=True, autoload_with=engine)
    query = db.select([products_table]).where(
        products_table.columns.title == 'Test product')
    result = connection.execute(query).fetchall()

    query = db.select([products_table])
    num_of_products = len(connection.execute(query).fetchall())
    response = client.get("/products")

    assert response.status_code == 200
    assert len(response.json()) == num_of_products
    assert test_product['title'] in [prod['title'] for prod in response.json()]


def test_get_product(create_and_delete_test_product_oracle):
    connection = engine.connect()
    products_table = db.Table(
        'products', db.MetaData(), autoload=True, autoload_with=engine)
    query = db.select([products_table]).where(
        products_table.columns.title == 'Test product')
    result = connection.execute(query).fetchall()[0]
    response = client.get(f"/products/{result[0]}")

    assert response.status_code == 200
    for key in test_product:
        if key in ['_id', 'added_at']:
            continue
        assert response.json()[key] == test_product[key]


def test_post_products(delete_test_product):
    test_prod = test_product.copy()
    test_prod.pop('added_at', None)
    test_prod.pop('_id', None)
    response = client.post(f"/products/", json=test_prod)
    assert response.status_code == 200

    connection = engine.connect()
    products_table = db.Table(
        'products', db.MetaData(), autoload=True, autoload_with=engine)
    query = db.select([products_table]).where(
        products_table.columns.title == 'Test product')
    result = connection.execute(query).fetchall()[0]
    mongo_product = mongoDB.products.find_one({'title': 'Test product'})

    assert result[0] == mongo_product['_id']
    assert result[1] == test_prod['title']


def test_post_orders(create_product_and_fully_delete_order):
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
    orders_table = db.Table('orders', db.MetaData(),
                            autoload=True, autoload_with=engine)
    query = db.select([orders_table]).where(
        orders_table.columns.query == 'test query')
    result = connection.execute(query).fetchall()[0]
    mongo_order = mongoDB.orders.find_one({'query': 'test query'})

    for key, val in test_order.items():
        if key in ['_id', 'added_at']:
            continue
        assert val == test_order[key]
        assert mongo_order[key] == test_order[key]


def test_put_product(create_and_delete_test_product_oracle, create_and_delete_test_product):
    test_product.pop('added_at', None)
    connection = engine.connect()
    products_table = db.Table(
        'products', db.MetaData(), autoload=True, autoload_with=engine)
    query = db.select([products_table]).where(
        products_table.columns.title == 'Test product')
    db_product = connection.execute(query).fetchall()[0]

    test_product['title'] = "Test product EDITED"
    response = client.put(f"/products/{db_product[0]}", json=test_product)
    assert response.status_code == 200

    query = db.select([products_table]).where(
        products_table.columns.title == 'Test product EDITED')
    new_db_product = connection.execute(query).fetchall()[0]
    mongo_product = mongoDB.products.find_one({'title': 'Test product EDITED'})

    for original, new in zip(db_product[2:-1], new_db_product[2:-1]):
        assert original == new
        assert new in mongo_product.values()


def test_buy_product_new_order(create_and_delete_test_product, create_and_delete_test_product_oracle):
    body = {
        "user_information": "test user info",
        "transport_information": "test transport info",
        "query": "test query",
    }
    response = client.put(
        f"/products/buy/{test_product['_id']}", params={'count': 2}, json=body)
    assert response.status_code == 200

    # check that order was created
    connection = engine.connect()
    orders_table = db.Table('orders', db.MetaData(),
                            autoload=True, autoload_with=engine)
    query = db.select([orders_table]).where(
        orders_table.columns.query == 'test query')
    oracle_order = connection.execute(query).fetchall()[0]
    mongo_order = mongoDB.orders.find_one({'query': 'test query'})

    order_product_table = db.Table(
        'order_product', db.MetaData(), autoload=True, autoload_with=engine)
    query = db.select([order_product_table]).where(
        order_product_table.columns.product_id == test_product['_id'])
    order_product = connection.execute(query).fetchall()[0]
    assert order_product[0] == test_product['_id']
    assert order_product[1] == oracle_order['_id']
    assert order_product[1] == mongo_order['_id']
    assert order_product[2] == 2  # count

    # cleanup
    query = db.delete(order_product_table).where(
        order_product_table.columns.product_id == test_product['_id'])
    connection.execute(query)
    query = db.delete(orders_table).where(
        orders_table.columns._id == oracle_order['_id'])
    connection.execute(query)
    mongoDB.orders.delete_many({'_id': mongo_order['_id']})


def test_buy_product_existing_order(create_and_delete_order_product):
    body = {
        "user_information": "test user info",
        "transport_information": "test transport info",
        "query": "test query",
    }
    params = {'count': 2, 'order_id': test_order['_id']}
    response = client.put(
        f"/products/buy/{test_product['_id']}", params=params, json=body)
    assert response.status_code == 200

    connection = engine.connect()
    order_product_table = db.Table(
        'order_product', db.MetaData(), autoload=True, autoload_with=engine)
    query = db.select([order_product_table]).where(
        order_product_table.columns.order_id == test_order['_id'])
    order_products = connection.execute(query).fetchall()
    assert (test_product['_id'], test_order['_id'], 2) in order_products

    mongo_prod1 = mongoDB.products.find_one({'_id': test_product['_id']})
    assert mongo_prod1['in_stock'] == test_product['in_stock'] - 2

    # cleanup
    query = db.delete(order_product_table).where(
        order_product_table.columns.order_id == test_order['_id'])
    connection.execute(query)


def test_buy_product_non_exist():
    body = {
        "user_information": "test user info",
        "transport_information": "test transport info",
        "query": "test query",
    }
    params = {'count': 2, 'order_id': test_order['_id']}
    response = client.put("/products/buy/111111111111111111111", params=params, json=body)
    assert response.status_code == 400
    assert response.json()['detail'] == "Product doesn't exist"


def test_buy_product_not_in_stock(create_and_delete_test_product_oracle):
    body = {
        "user_information": "test user info",
        "transport_information": "test transport info",
        "query": "test query",
    }
    params = {'count': 5, 'order_id': test_order['_id']}
    response = client.put(f"/products/buy/{test_product['_id']}", params=params, json=body)
    assert response.status_code == 400
    assert response.json()['detail'] == \
    f"""Not enough products in store. Requested: 5, In stock: {test_product['in_stock']}"""


def test_buy_product_zero(create_and_delete_test_product_oracle):
    body = {
        "user_information": "test user info",
        "transport_information": "test transport info",
        "query": "test query",
    }
    params = {'count': 0, 'order_id': test_order['_id']}
    response = client.put(f"/products/buy/{test_product['_id']}", params=params, json=body)
    assert response.status_code == 400
    assert response.json()['detail'] == "0 is incorrect number of products to buy"


def test_buy_product_non_exist_order(create_and_delete_test_product_oracle):
    body = {
        "user_information": "test user info",
        "transport_information": "test transport info",
        "query": "test query",
    }
    params = {'count': 2, 'order_id': 11111111111111}
    response = client.put(f"/products/buy/{test_product['_id']}", params=params, json=body)
    assert response.status_code == 400
    assert response.json()['detail'] == "Order doesn't exist"




if __name__ == '__main__':
    mongoDB.orders.delete_many({})
    mongoDB.products.delete_many({'_id': 69696969})
    mongoDB.products.delete_many({'_id': 13371337})
    mongoDB.products.delete_many({'title': 'Test product'})
