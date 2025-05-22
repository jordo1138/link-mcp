import pytest
from app.services.stripe_detector import (
    is_stripe_enabled,
    _detect_stripe_js,
    _detect_stripe_checkout,
    _detect_stripe_elements
)
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup

# Mock HTML with Stripe integration
STRIPE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://js.stripe.com/v3/"></script>
</head>
<body>
    <form>
        <div id="card-element"></div>
        <button>Pay Now</button>
    </form>
    <script>
        const stripe = Stripe('pk_test_123');
        const elements = stripe.elements();
        const card = elements.create('card');
        card.mount('#card-element');
    </script>
</body>
</html>
"""

# Mock HTML without Stripe integration
NON_STRIPE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://example.com/js/payment.js"></script>
</head>
<body>
    <form action="/process-payment">
        <input type="text" name="cc-number">
        <button>Pay Now</button>
    </form>
</body>
</html>
"""

@pytest.fixture
def stripe_soup():
    return BeautifulSoup(STRIPE_HTML, 'html.parser')

@pytest.fixture
def non_stripe_soup():
    return BeautifulSoup(NON_STRIPE_HTML, 'html.parser')

def test_detect_stripe_js_positive(stripe_soup):
    assert _detect_stripe_js(STRIPE_HTML, stripe_soup) > 0.0

def test_detect_stripe_js_negative(non_stripe_soup):
    assert _detect_stripe_js(NON_STRIPE_HTML, non_stripe_soup) == 0.0

def test_detect_stripe_elements_positive(stripe_soup):
    assert _detect_stripe_elements(STRIPE_HTML, stripe_soup) > 0.0

def test_detect_stripe_elements_negative(non_stripe_soup):
    assert _detect_stripe_elements(NON_STRIPE_HTML, non_stripe_soup) == 0.0

@patch('requests.get')
def test_is_stripe_enabled_positive(mock_get, stripe_soup):
    # Configure the mock to return a response with Stripe HTML
    mock_response = MagicMock()
    mock_response.text = STRIPE_HTML
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    result = is_stripe_enabled('https://example.com/product')
    
    assert result['stripe_enabled'] is True
    assert result['confidence'] > 0.3

@patch('requests.get')
def test_is_stripe_enabled_negative(mock_get, non_stripe_soup):
    # Configure the mock to return a response without Stripe HTML
    mock_response = MagicMock()
    mock_response.text = NON_STRIPE_HTML
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    result = is_stripe_enabled('https://example.com/product')
    
    assert result['stripe_enabled'] is False

@patch('requests.get')
def test_is_stripe_enabled_exception(mock_get):
    # Configure the mock to raise an exception
    mock_get.side_effect = Exception("Connection error")
    
    result = is_stripe_enabled('https://example.com/product')
    
    assert result['stripe_enabled'] is False
    assert result['confidence'] == 0
    assert 'Connection error' in result['details']['error']