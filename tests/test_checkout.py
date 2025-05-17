import sys
import types

stripe_stub = types.ModuleType("stripe")
stripe_stub.Product = types.SimpleNamespace(retrieve=lambda *a, **k: None)
stripe_stub.checkout = types.SimpleNamespace(Session=types.SimpleNamespace(create=lambda **k: None))
sys.modules.setdefault("stripe", stripe_stub)

from app.services.checkout import create_link_checkout_session


import os


def test_create_link_checkout_session_no_api_key():
    os.environ["STRIPE_API_KEY"] = ""
    import app.services.checkout as checkout
    checkout.stripe.api_key = os.environ["STRIPE_API_KEY"]
    session = create_link_checkout_session("prod_123", "s", "c")
    assert session is None


def test_create_link_checkout_session_success():
    os.environ["STRIPE_API_KEY"] = "sk_test"

    class DummySession:
        def __init__(self):
            self.url = "https://checkout.stripe.com/session"

        def to_dict_recursive(self):
            return {"url": self.url}

    dummy_product = type("Product", (), {"default_price": {"id": "price_123"}})()

    stripe_stub.Product.retrieve = lambda pid, expand=None: dummy_product
    stripe_stub.checkout.Session.create = lambda **kwargs: DummySession()
    import app.services.checkout as checkout
    checkout.stripe.api_key = os.environ["STRIPE_API_KEY"]

    session = create_link_checkout_session("prod_123", "s", "c")
    assert session == {"url": "https://checkout.stripe.com/session"}
