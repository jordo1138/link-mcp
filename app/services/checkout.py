import os
import stripe

stripe.api_key = os.environ.get("STRIPE_API_KEY", "")


def create_link_checkout_session(product_id: str, success_url: str, cancel_url: str):
    """Create a Stripe Checkout session for Link."""
    if not stripe.api_key:
        return None

    product = stripe.Product.retrieve(product_id, expand=["default_price"])
    price = getattr(product, "default_price", None)
    if not price:
        return None

    price_id = price["id"] if isinstance(price, dict) else price.id
    session = stripe.checkout.Session.create(
        payment_method_types=["link"],
        mode="payment",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return session.to_dict_recursive()
