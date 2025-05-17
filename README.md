# link-mcp

This repository contains a simple Flask server that exposes product information
from Stripe. The `/products/link` endpoint returns only products eligible for
Stripe Link checkout. Eligibility is determined via the product's metadata
field `link_eligible`.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set the `STRIPE_API_KEY` environment variable with your Stripe secret key.
3. Run the server:
   ```bash
   python server.py
   ```
