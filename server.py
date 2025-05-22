from flask import Flask, jsonify, request
import os
from app.services.stripe_detector import is_stripe_enabled
from app.services.product_validator import validate_products
from app.services.checkout_helper import generate_checkout_url

app = Flask(__name__)

@app.route('/api/validate-url', methods=['POST'])
def validate_url():
    """Check if a single URL uses Stripe for payments"""
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400
    
    result = is_stripe_enabled(data['url'])
    return jsonify({
        'url': data['url'],
        'stripe_enabled': result['stripe_enabled'],
        'confidence': result['confidence'],
        'details': result.get('details', {})
    })

@app.route('/api/filter-products', methods=['POST'])
def filter_products():
    """Filter a list of products to only those using Stripe"""
    data = request.get_json()
    if not data or 'products' not in data:
        return jsonify({'error': 'Product list is required'}), 400
    
    filtered = validate_products(data['products'])
    return jsonify({
        'total': len(data['products']),
        'stripe_enabled': len(filtered),
        'products': filtered
    })

@app.route('/api/checkout', methods=['POST'])
def create_checkout():
    """Generate a checkout URL for a Stripe-enabled product"""
    data = request.get_json()
    if not data or 'product_url' not in data:
        return jsonify({'error': 'Product URL is required'}), 400
    
    checkout_url = generate_checkout_url(
        data['product_url'],
        success_url=data.get('success_url', 'https://example.com/success'),
        cancel_url=data.get('cancel_url', 'https://example.com/cancel')
    )
    
    if not checkout_url:
        return jsonify({'error': 'Unable to generate checkout URL'}), 400
    
    return jsonify({
        'checkout_url': checkout_url
    })

if __name__ == '__main__':
    app.run(debug=True)