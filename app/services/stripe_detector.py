import re
import requests
import json
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import time
from typing import Dict, Any

# Cache of already checked sites
site_cache = {}

def is_stripe_enabled(url: str) -> Dict[str, Any]:
    """Determine if a website uses Stripe for payment processing.
    
    Args:
        url: The URL of the product or website to check
        
    Returns:
        Dictionary with results including:
        - stripe_enabled: Boolean indicating if Stripe was detected
        - confidence: Float between 0-1 indicating confidence level
        - details: Additional information about detection
    """
    # Normalize URL to get domain
    parsed = urlparse(url)
    domain = parsed.netloc
    
    # Check cache first
    if domain in site_cache:
        cache_entry = site_cache[domain]
        # If entry is less than 24 hours old, return it
        if time.time() - cache_entry['timestamp'] < 86400:
            return cache_entry['result']
    
    try:
        # Fetch the page with a more realistic browser user-agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        
        # Detection methods and their confidence weights
        detection_results = {
            'stripe_js': _detect_stripe_js(html, soup),
            'stripe_checkout': _detect_stripe_checkout(html, soup),
            'stripe_elements': _detect_stripe_elements(html, soup),
            'stripe_links': _detect_stripe_links(html, soup),
            'payment_request_button': _detect_payment_request_button(html, soup),
            'stripe_keywords': _detect_stripe_keywords(html, soup),
            'stripe_json_data': _detect_stripe_json_data(html, soup),
            'stripe_metadata': _detect_stripe_metadata(soup)
        }
        
        # For popular e-commerce platforms, check for known Stripe implementations
        platform_check = _check_popular_platforms(url, soup, html)
        if platform_check > 0:
            detection_results['platform_specific'] = platform_check
            
        # Calculate overall confidence
        confidence = sum(detection_results.values()) / len(detection_results)
        
        # Determine if Stripe is enabled based on confidence threshold
        stripe_enabled = confidence > 0.15  # Lower threshold to catch more potential matches
        
        # If we're on a checkout page, be more lenient
        if '/checkout' in url.lower() and any(val > 0 for val in detection_results.values()):
            stripe_enabled = True
            confidence = max(confidence, 0.4)  # Set minimum confidence for checkout pages
        
        result = {
            'stripe_enabled': stripe_enabled,
            'confidence': round(confidence, 2),
            'details': {
                'detection_methods': detection_results,
                'timestamp': int(time.time())
            }
        }
        
        # Cache the result
        site_cache[domain] = {
            'timestamp': time.time(),
            'result': result
        }
        
        return result
    
    except Exception as e:
        return {
            'stripe_enabled': False,
            'confidence': 0,
            'details': {
                'error': str(e),
                'timestamp': int(time.time())
            }
        }

def _detect_stripe_js(html: str, soup: BeautifulSoup) -> float:
    """Check for Stripe.js inclusion"""
    stripe_js_patterns = [
        r'https://js\.stripe\.com/v3',
        r'stripe\.com/v3',
        r'Stripe\(.*\)',
        r'stripe-js',
        r'loadStripe',
        r'stripeElements',
        r'stripe\.initialize',
        r'stripe_payment_elements',
        r'stripePromise'
    ]
    
    for pattern in stripe_js_patterns:
        if re.search(pattern, html, re.IGNORECASE):
            return 1.0
    
    # Check script tags
    for script in soup.find_all('script'):
        src = script.get('src', '')
        if src and ('stripe' in src.lower() or 'pay' in src.lower()):
            return 0.8
            
        # Check script content
        if script.string and 'stripe' in script.string.lower():
            return 0.9
    
    return 0.0

def _detect_stripe_checkout(html: str, soup: BeautifulSoup) -> float:
    """Check for Stripe Checkout"""
    checkout_patterns = [
        r'redirectToCheckout',
        r'stripe\.redirectToCheckout',
        r'checkout\.stripe\.com',
        r'pay\.stripe\.com',
        r'billing\.stripe\.com',
        r'stripe_checkout'
    ]
    
    for pattern in checkout_patterns:
        if re.search(pattern, html, re.IGNORECASE):
            return 1.0
    
    # Check for checkout form with data attributes
    checkout_forms = soup.find_all(['form', 'div'], attrs={'data-processor': re.compile('stripe', re.IGNORECASE)})
    if checkout_forms:
        return 1.0
    
    return 0.0

def _detect_stripe_elements(html: str, soup: BeautifulSoup) -> float:
    """Check for Stripe Elements"""
    elements_patterns = [
        r'stripe\.elements\(\)',
        r'Elements\(',
        r'card-element',
        r'CardElement',
        r'PaymentElement',
        r'StripeElement',
        r'stripe-card-element',
        r'data-stripe',
        r'card_element',
        r'payment-element',
        r'stripe-elements'
    ]
    
    for pattern in elements_patterns:
        if re.search(pattern, html, re.IGNORECASE):
            return 1.0
    
    # Check for div elements that might be Stripe Elements containers
    for div in soup.find_all(['div', 'span', 'iframe']):
        div_id = div.get('id', '').lower()
        div_class = ' '.join(div.get('class', [])).lower()
        div_data = str(div.get('data-', '')).lower()
        
        if any(term in div_id or term in div_class or term in div_data 
               for term in ['card', 'stripe', 'payment', 'checkout']):
            return 0.7
    
    return 0.0

def _detect_stripe_links(html: str, soup: BeautifulSoup) -> float:
    """Check for Stripe-related links or forms"""
    # Check form actions
    for form in soup.find_all('form'):
        action = form.get('action', '')
        if 'stripe' in action.lower():
            return 1.0
        
        # Check form data attributes
        for attr_name, attr_value in form.attrs.items():
            if attr_name.startswith('data-') and ('stripe' in attr_value.lower() if isinstance(attr_value, str) else False):
                return 0.9
    
    # Check links
    for a in soup.find_all('a', href=True):
        if 'stripe' in a['href'].lower():
            return 0.7
    
    return 0.0

def _detect_payment_request_button(html: str, soup: BeautifulSoup) -> float:
    """Check for Stripe Payment Request Button"""
    prb_patterns = [
        r'paymentRequestButton',
        r'PaymentRequest',
        r'payment-request-button',
        r'payment_request',
        r'apple-pay',
        r'google-pay',
        r'stripe-payment-request'
    ]
    
    for pattern in prb_patterns:
        if re.search(pattern, html, re.IGNORECASE):
            return 1.0
    
    return 0.0

def _detect_stripe_keywords(html: str, soup: BeautifulSoup) -> float:
    """Check for Stripe-related keywords in content"""
    keyword_patterns = [
        # Stripe-specific terminology
        r'stripe\.js',
        r'stripe integration',
        r'stripe gateway',
        r'stripe api',
        r'stripe token',
        r'stripe payment',
        r'credit card.{0,30}(details|information|number|cvv|cvc)', 
        r'payment method.{0,30}stripe',
        r'stripe_version'
    ]
    
    # Check meta tags for payment hints
    for meta in soup.find_all('meta'):
        content = meta.get('content', '').lower()
        if 'payment' in content and any(word in content for word in ['method', 'gateway', 'processor', 'stripe']):
            return 0.8
    
    # Check for specific patterns
    for pattern in keyword_patterns:
        if re.search(pattern, html, re.IGNORECASE):
            return 0.6
    
    # Look for payment icons or images
    for img in soup.find_all('img'):
        src = img.get('src', '').lower()
        alt = img.get('alt', '').lower()
        if 'stripe' in src or 'stripe' in alt:
            return 0.7
    
    return 0.0

def _detect_stripe_json_data(html: str, soup: BeautifulSoup) -> float:
    """Look for Stripe information in JSON data on the page"""
    # Find JSON data in script tags
    for script in soup.find_all('script', type=lambda t: t and ('json' in t or 'application/ld+json' in t)):
        if not script.string:
            continue
            
        try:
            data = json.loads(script.string)
            
            # Recursively search for Stripe-related strings in the JSON
            def search_json(obj, search_term):
                if isinstance(obj, dict):
                    return any(search_json(v, search_term) for v in obj.values()) or \
                           any(search_term in k.lower() for k in obj.keys() if isinstance(k, str))
                elif isinstance(obj, list):
                    return any(search_json(item, search_term) for item in obj)
                elif isinstance(obj, str):
                    return search_term in obj.lower()
                return False
                
            if search_json(data, 'stripe'):
                return 1.0
            if search_json(data, 'payment') or search_json(data, 'checkout'):
                return 0.4
        except:
            # Not valid JSON or other error
            pass
    
    # Check for JSON in data attributes
    for elem in soup.find_all(attrs={"data-json": True}):
        try:
            data = json.loads(elem["data-json"])
            if search_json(data, 'stripe'):
                return 1.0
        except:
            pass
            
    return 0.0

def _detect_stripe_metadata(soup: BeautifulSoup) -> float:
    """Check for Stripe metadata in HTML attributes"""
    # Look for data attributes related to payments
    payment_data_elements = soup.find_all(lambda tag: any(attr.startswith('data-') and (
        'payment' in attr.lower() or 
        'stripe' in attr.lower() or
        'checkout' in attr.lower()
    ) for attr in tag.attrs))
    
    if payment_data_elements:
        return 0.7
    
    # Check for Stripe-specific class naming patterns
    stripe_class_elements = soup.find_all(class_=lambda c: c and any(
        pattern in c.lower() for pattern in [
            'stripe', 'payment', 'checkout', 'card-', 'pay-'
        ]
    ))
    
    if stripe_class_elements:
        return 0.5
        
    return 0.0

def _check_popular_platforms(url: str, soup: BeautifulSoup, html: str) -> float:
    """Check for known e-commerce platforms that commonly use Stripe"""
    # Check for Shopify with Stripe
    if ('shopify' in html.lower() or 'cdn.shopify.com' in html) and \
       ('stripe' in html.lower() or 'payment' in html.lower()):
        return 0.8
        
    # Check for WooCommerce with Stripe
    if 'woocommerce' in html.lower():
        if 'wc-stripe' in html.lower() or 'stripe_checkout' in html.lower():
            return 0.9
            
    # Check for BigCommerce with Stripe
    if 'bigcommerce' in html.lower() and 'stripe' in html.lower():
        return 0.8
        
    # Check for Webflow with Stripe
    if 'webflow' in html.lower() and 'stripe' in html.lower():
        return 0.8
    
    # Check if the site is a SaaS checkout page (like Eight Sleep, Casper, etc.)
    checkout_indicators = [
        'checkout-container', 
        'checkout_page',
        'checkout-section',
        'order summary',
        'payment information',
        'billing information',
        'card information'
    ]
    
    if '/checkout' in url.lower() and any(indicator in html.lower() for indicator in checkout_indicators):
        # If it's a checkout page with payment fields, there's a good chance it uses Stripe
        payment_fields = soup.find_all(['input', 'div'], attrs={
            'name': lambda n: n and any(term in n.lower() for term in ['card', 'cc-', 'credit', 'payment'])
        })
        if payment_fields:
            return 0.6
            
    # Final check for Stripe in any form
    if 'stripe' in html.lower():
        return 0.5
            
    return 0.0