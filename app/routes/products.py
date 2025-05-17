from flask import Blueprint, jsonify
from app.services.product_query import list_products
from app.services.link_filter import filter_link_eligible

products_bp = Blueprint('products', __name__)


@products_bp.route('/products/link', methods=['GET'])
def get_link_products():
    products = list_products()
    link_products = filter_link_eligible(products)
    return jsonify(link_products)
