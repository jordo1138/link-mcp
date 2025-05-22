from typing import List, Dict, Any
from app.services.stripe_detector import is_stripe_enabled
from urllib.parse import urlparse
import json
import os
import time

# Cache file path for validated products
_ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_CACHE_PATH = os.path.join(_ROOT_DIR, "data", "validated_sites.json")

# Load cache if it exists
site_validation_cache = {}
if os.path.exists(_CACHE_PATH):
    try:
        with open(_CACHE_PATH, "r", encoding="utf-8") as f:
            site_validation_cache = json.load(f)
    except:
        # If loading fails, start with empty cache
        site_validation_cache = {}

def validate_products(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter a list of products to only those using Stripe for payment.
    
    Args:
        products: List of product dictionaries, each containing at least a 'url' key
        
    Returns:
        Filtered list of products that use Stripe for payment
    """
    # Make sure cache directory exists
    os.makedirs(os.path.dirname(_CACHE_PATH), exist_ok=True)
    
    stripe_products = []
    for product in products:
        # Skip products without URLs
        if 'url' not in product:
            continue
            
        url = product['url']
        domain = urlparse(url).netloc
        
        # Check if domain is in cache
        if domain in site_validation_cache:
            cache_entry = site_validation_cache[domain]
            # Use cache if less than 24 hours old
            if time.time() - cache_entry['timestamp'] < 86400:
                if cache_entry['stripe_enabled']:
                    stripe_products.append(product)
                continue
        
        # Check for Stripe integration
        result = is_stripe_enabled(url)
        
        # Update cache
        site_validation_cache[domain] = {
            'stripe_enabled': result['stripe_enabled'],
            'confidence': result['confidence'],
            'timestamp': time.time()
        }
        
        # Save to disk occasionally (every 10 new validations)
        if len(site_validation_cache) % 10 == 0:
            try:
                with open(_CACHE_PATH, "w", encoding="utf-8") as f:
                    json.dump(site_validation_cache, f, indent=2)
            except Exception as e:
                print(f"Error saving cache: {e}")
        
        # Add to results if Stripe-enabled
        if result['stripe_enabled']:
            # Add Stripe information to the product
            product['stripe_info'] = {
                'confidence': result['confidence'],
                'validated_at': int(time.time())
            }
            stripe_products.append(product)
    
    # Save cache after processing
    try:
        with open(_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(site_validation_cache, f, indent=2)
    except Exception as e:
        print(f"Error saving cache: {e}")
            
    return stripe_products