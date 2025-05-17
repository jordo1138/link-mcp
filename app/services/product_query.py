import os
import stripe

stripe.api_key = os.environ.get("STRIPE_API_KEY", "")


def list_products(limit: int = 10):
    """Retrieve products from Stripe."""
    if not stripe.api_key:
        return []
    resp = stripe.Product.list(limit=limit, expand=["data.default_price"])
    products = [p.to_dict_recursive() for p in resp.data]
    return products
