import json
import os
import requests
from typing import Optional, Dict, Any
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from app.services.stripe_detector import is_stripe_enabled

# Cache for direct checkout links
_ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_CHECKOUT_CACHE_PATH = os.path.join(_ROOT_DIR, "data", "checkout_links.json")

# Load checkout cache if exists
checkout_cache = {}
if os.path.exists(_CHECKOUT_CACHE_PATH):
    try:
        with open(_CHECKOUT_CACHE_PATH, "r", encoding="utf-8") as f:
            checkout_cache = json.load(f)
    except:
        checkout_cache = {}

def generate_checkout_url(product_url: str, success_url: str = '', cancel_url: str = '') -> Optional[str]:
    """Generate a direct checkout URL for a Stripe-enabled product.
    
    This function attempts to find the most direct way to purchase a product
    using Stripe checkout, either by:
    1. Finding a direct "Buy Now" button that leads to Stripe Checkout
    2. Finding an "Add to Cart" button and simulating the checkout process
    3. For supported platforms (Shopify, WooCommerce), using their direct checkout APIs
    
    Args:
        product_url: URL of the product page
        success_url: Optional URL to redirect after successful purchase
        cancel_url: Optional URL to redirect after cancelled purchase
        
    Returns:
        A direct checkout URL, or None if unable to generate one
    """
    # Check if product uses Stripe first
    stripe_check = is_stripe_enabled(product_url)
    if not stripe_check['stripe_enabled']:
        return None
    
    # Check if we have a cached checkout link
    if product_url in checkout_cache:
        return checkout_cache[product_url]['checkout_url']
    
    # Try to determine the e-commerce platform
    platform = _detect_platform(product_url)
    
    checkout_url = None
    
    if platform == 'shopify':
        checkout_url = _handle_shopify_checkout(product_url)
    elif platform == 'woocommerce':
        checkout_url = _handle_woocommerce_checkout(product_url)
    else:
        # Generic approach - try to find direct checkout links
        checkout_url = _find_checkout_link(product_url)
    
    if checkout_url:
        # Cache the checkout URL
        checkout_cache[product_url] = {
            'checkout_url': checkout_url,
            'platform': platform
        }
        
        # Save cache
        try:
            os.makedirs(os.path.dirname(_CHECKOUT_CACHE_PATH), exist_ok=True)
            with open(_CHECKOUT_CACHE_PATH, "w", encoding="utf-8") as f:
                json.dump(checkout_cache, f, indent=2)
        except Exception as e:
            print(f"Error saving checkout cache: {e}")
    
    return checkout_url

def _detect_platform(url: str) -> str:
    """Detect the e-commerce platform used by the website."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        html = response.text
        
        # Check for Shopify
        if 'Shopify.theme' in html or '/cdn.shopify.com/' in html:
            return 'shopify'
        
        # Check for WooCommerce
        if 'woocommerce' in html.lower() or 'add-to-cart' in html.lower():
            return 'woocommerce'
        
        # Add more platform detection as needed
        
        return 'unknown'
    except:
        return 'unknown'

def _handle_shopify_checkout(url: str) -> Optional[str]:
    """Generate a direct checkout URL for Shopify stores."""
    try:
        # Parse URL to get domain
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # Extract product details
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for product JSON
        for script in soup.find_all('script', type='application/json'):
            if 'ProductJson' in script.get('id', ''):
                product_data = json.loads(script.string)
                variant_id = product_data.get('variants', [{}])[0].get('id')
                if variant_id:
                    # Create direct checkout URL
                    checkout_url = f"https://{domain}/cart/{variant_id}:1"
                    return checkout_url
        
        # Alternative method - find add to cart form
        form = soup.find('form', action=lambda x: x and '/cart/add' in x)
        if form:
            variant_input = form.find('input', {'name': 'id'})
            if variant_input and variant_input.get('value'):
                variant_id = variant_input['value']
                checkout_url = f"https://{domain}/cart/{variant_id}:1"
                return checkout_url
    except Exception as e:
        print(f"Error generating Shopify checkout: {e}")
    
    return None

def _handle_woocommerce_checkout(url: str) -> Optional[str]:
    """Generate a direct checkout URL for WooCommerce stores."""
    try:
        # Get the page content
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find add to cart form
        add_to_cart_form = soup.find('form', {'class': 'cart'})
        if add_to_cart_form:
            product_id = None
            # Look for product ID input
            product_input = add_to_cart_form.find('input', {'name': 'add-to-cart'})
            if product_input:
                product_id = product_input.get('value')
            
            if product_id:
                # Create direct checkout URL
                base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
                checkout_url = f"{base_url}/checkout/?add-to-cart={product_id}&quantity=1"
                return checkout_url
    except Exception as e:
        print(f"Error generating WooCommerce checkout: {e}")
    
    return None

def _find_checkout_link(url: str) -> Optional[str]:
    """Generic method to find checkout links on a product page."""
    try:
        # Get the page content
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        
        # Look for common checkout or buy now buttons
        buy_selectors = [
            {'tag': 'a', 'text': ['buy now', 'checkout', 'purchase']},
            {'tag': 'button', 'text': ['buy now', 'checkout', 'purchase']},
            {'tag': 'a', 'class': ['buy', 'checkout', 'purchase', 'btn-buy']},
            {'tag': 'button', 'class': ['buy', 'checkout', 'purchase', 'btn-buy']},
        ]
        
        for selector in buy_selectors:
            tag = selector['tag']
            
            # Check by text content
            if 'text' in selector:
                for text in selector['text']:
                    elements = soup.find_all(tag, string=lambda s: s and text.lower() in s.lower())
                    for element in elements:
                        if tag == 'a' and element.get('href'):
                            return urljoin(base_url, element['href'])
                        elif tag == 'button' and element.get('onclick'):
                            # Try to extract URL from onclick
                            onclick = element['onclick']
                            if 'location' in onclick and 'http' in onclick:
                                url_match = re.search(r'(["\'])(?:http|/).*?\1', onclick)
                                if url_match:
                                    url_str = url_match.group(0).strip('"\'')
                                    return urljoin(base_url, url_str)
            
            # Check by class
            if 'class' in selector:
                for class_name in selector['class']:
                    elements = soup.find_all(tag, class_=lambda c: c and class_name.lower() in c.lower())
                    for element in elements:
                        if tag == 'a' and element.get('href'):
                            return urljoin(base_url, element['href'])
        
        # Look for checkout forms
        checkout_forms = soup.find_all('form', action=lambda a: a and ('checkout' in a.lower() or 'cart' in a.lower()))
        if checkout_forms:
            return urljoin(base_url, checkout_forms[0]['action'])
    
    except Exception as e:
        print(f"Error finding checkout link: {e}")
    
    return None