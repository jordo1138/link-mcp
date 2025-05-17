from flask import Blueprint, jsonify, request
from app.services.product_query import list_products
from app.services.link_filter import filter_link_eligible
from app.services.checkout import create_link_checkout_session

products_bp = Blueprint('products', __name__)


@products_bp.route('/products/link', methods=['GET'])
def get_link_products():
    products = list_products()
    link_products = filter_link_eligible(products)
    return jsonify(link_products)


@products_bp.route('/products/<product_id>/buy', methods=['POST'])
def buy_product(product_id):
    """Create a Link Checkout session for the selected product."""
    data = request.get_json(silent=True) or {}
    success_url = data.get('success_url', 'https://example.com/success')
    cancel_url = data.get('cancel_url', 'https://example.com/cancel')
    session = create_link_checkout_session(product_id, success_url, cancel_url)
    if not session:
        return jsonify({'error': 'Unable to create checkout session'}), 500
    return jsonify({'checkout_url': session['url']})
