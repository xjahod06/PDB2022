pytest -v test_mongo.py::test_get_product && 
pytest -v test_mongo.py::test_get_product_not_exist && 
pytest -v test_mongo.py::test_get_products && 
pytest -v test_mongo.py::test_delete_product && 
pytest -v test_mongo.py::test_delete_product_not_exist && 
pytest -v test_mongo.py::test_price_range && 
pytest -v test_mongo.py::test_in_stock_range && 
pytest -v test_mongo.py::test_get_by_brand && 
pytest -v test_mongo.py::test_in_description && 
pytest -v test_mongo.py::test_in_description_incorrect &&
pytest -v test_mongo.py::test_get_orders && 
pytest -v test_mongo.py::test_get_order && 
pytest -v test_mongo.py::test_get_order_not_exist