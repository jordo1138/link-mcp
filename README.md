# Stripe-MCP: Model Context Protocol for Stripe-enabled Products

Stripe-MCP is a Model Context Protocol (MCP) server that helps LLMs and AI shopping agents identify and filter products based on whether they use Stripe for payment processing. This enables agents to focus on sites where seamless checkout experiences are possible.

## Key Features

- **Stripe Detection**: Analyzes web pages to determine if they use Stripe for payments
- **Product Filtering**: Filters product lists to only include Stripe-enabled items
- **Checkout URL Generation**: Creates direct checkout links for supported platforms
- **Caching System**: Saves validation results to improve performance
- **MCP Compatible**: Follows Model Context Protocol for easy LLM integration

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the server:
   ```bash
   python server.py
   ```

## API Endpoints

### Validate URL

```
POST /api/validate-url
Body: {"url": "https://example.com/product"}
```

Checks if a website uses Stripe for payment processing.

### Filter Products

```
POST /api/filter-products
Body: {"products": [{"url": "https://example.com/product", "name": "Example Product", ...}]}
```

Filters a list of products to only include those using Stripe.

### Generate Checkout URL

```
POST /api/checkout
Body: {
  "product_url": "https://example.com/product",
  "success_url": "https://yourdomain.com/success",
  "cancel_url": "https://yourdomain.com/cancel"
}
```

Generates a direct checkout URL for a Stripe-enabled product.

## For AI Agents

AI shopping assistants can use this MCP server to:

1. Validate if products found via web search use Stripe for payment
2. Filter product recommendations to only include Stripe-enabled merchants
3. Generate direct checkout links for a seamless purchasing experience

## Testing

Run the tests with:

```bash
python -m pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.