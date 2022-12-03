import configparser
from datetime import datetime

from fastapi.testclient import TestClient
import pytest

from api_mongo import app
from db_connect import *


config = configparser.ConfigParser()
config.read('config.conf')
client = TestClient(app)

mongoDB = connect_to_mongo(
    config['mongo_db']['name'], config['mongo_db']['password'])

test_product = {
    "_id": 123456789987654321,
    "title": "Test product",
    "images": "https://test.product.url",
    "description": "This is a description of an abstract test product",
    "sku": 1111111111,
    "gtin13": 111111111111,
    "brand": "Test brand",
    "price": 69,
    "currency": "USD",
    "in_stock": 2,
    "added_at": datetime.now()
}

test_order = {
    '_id': 123456789987654321,
    'status': "Test order status",
    'price': 69,
    'created_at': datetime.now(),
    'user_information': "test user info",
    'transport_information': "test transport info",
    'query': "test query",
}


# setup and teardown
@pytest.fixture
def create_and_delete_test_product():
    mongoDB.products.insert_one(test_product)
    yield test_product
    mongoDB.products.delete_one({"title": "Test product"})


@pytest.fixture
def create_and_delete_test_order():
    mongoDB.orders.insert_one(test_order)
    yield test_order
    mongoDB.orders.delete_one({"_id": 123456789987654321})


# ============================TESTS==================================
def test_get_products(create_and_delete_test_product):
    num_of_products = mongoDB.products.count_documents({})
    response = client.get("/products")
    assert response.status_code == 200
    assert len(response.json()) == num_of_products
    assert test_product['title'] in [prod['title'] for prod in response.json()]


def test_get_product(create_and_delete_test_product):
    product = mongoDB.products.find_one({'title': 'Test product'})
    response = client.get(f"/products/{product['_id']}")
    assert response.status_code == 200
    for key in test_product:
        if key in ['_id', 'added_at']:
            continue
        assert response.json()[key] == test_product[key]


def test_get_product_not_exist():
    response = client.get(f"/products/123456789987654321")
    assert response.status_code == 404
    assert response.json() == {'detail': "Product not found"}


def test_delete_product(create_and_delete_test_product):
    product = mongoDB.products.find_one({'title': 'Test product'})
    response = client.delete(f"/products/{product['_id']}")
    assert response.status_code == 200
    assert response.json() == None
    product = mongoDB.products.find_one({'title': 'Test product'})
    assert product == None


def test_delete_product_not_exist(create_and_delete_test_product):
    response = client.delete(f"/products/0")
    assert response.status_code == 404
    assert response.json() == {'detail': "Product not found"}


def test_price_range(create_and_delete_test_product):
    response = client.get(f"/priceRange/", params={'gt': 60, 'lt': 70})
    assert response.status_code == 200
    for item in response.json():
        assert item['price'] > 60 and item['price'] < 70
    assert 'Test product' in [item['title'] for item in response.json()]


def test_in_stock_range(create_and_delete_test_product):
    response = client.get(f"/inStockRange/", params={'gt': 1, 'lt': 3})
    assert response.status_code == 200
    for item in response.json():
        assert item['in_stock'] > 1 and item['in_stock'] < 3
    assert 'Test product' in [item['title'] for item in response.json()]


def test_get_by_brand(create_and_delete_test_product):
    brand = "Test brand"
    response = client.get(f"/brand/{brand}")
    assert response.status_code == 200
    assert len(response.json()) == 1
    for key in test_product:
        if key in ['_id', 'added_at']:
            continue
        assert response.json()[0][key] == test_product[key]


def test_in_description(create_and_delete_test_product):
    key_word = "abstract test product"
    response = client.get(f"/inDescription/{key_word}")
    assert response.status_code == 200
    for key in test_product:
        if key in ['_id', 'added_at']:
            continue
        assert response.json()[key] == test_product[key]


def test_in_description_incorrect():
    key_word = "Non existing description"
    response = client.get(f"/inDescription/{key_word}")
    assert response.status_code == 200
    assert response.json() == None


def test_get_orders(create_and_delete_test_order):
    num_of_orders = mongoDB.orders.count_documents({})
    response = client.get("/orders")
    assert response.status_code == 200
    assert len(response.json()) == num_of_orders
    assert test_order['status'] in [order['status']
                                    for order in response.json()]


def test_get_order(create_and_delete_test_order):
    order = mongoDB.orders.find_one({'status': 'Test order status'})
    response = client.get(f"/orders/{order['_id']}")
    assert response.status_code == 200
    for key in test_order:
        if key in ['_id', 'created_at']:
            continue
        assert response.json()[key] == test_order[key]


def test_get_order_not_exist():
    response = client.get(f"/orders/123456789987654321")
    assert response.status_code == 404
    assert response.json() == {'detail': "Order not found"}


if __name__ == '__main__':
    mongoDB.products.delete_one({"title": "Test product"})
    mongoDB.orders.delete_one({"_id": 123456789987654321})
