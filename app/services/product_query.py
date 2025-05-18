import os
import json
import stripe

stripe.api_key = os.environ.get("STRIPE_API_KEY", "")


_ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_DB_PATH = os.path.join(_ROOT_DIR, "data", "product_urls.json")


def list_products(limit: int = 10):
    """Retrieve products from a local database of Link-enabled URLs."""
    if not os.path.exists(_DB_PATH):
        return []
    with open(_DB_PATH, "r", encoding="utf-8") as f:
        products = json.load(f)
    return products[:limit]
