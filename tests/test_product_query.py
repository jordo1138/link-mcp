import json
import tempfile
import app.services.product_query as pq


def test_list_products_returns_data_from_db():
    data = [{"id": "p1", "metadata": {"link_eligible": "true"}}]
    with tempfile.NamedTemporaryFile("w+", delete=False) as tmp:
        json.dump(data, tmp)
        tmp.flush()
        pq._DB_PATH = tmp.name
        products = pq.list_products()
    assert products == data
