# link-mcp

Link MCP is a Minimal Checkout Protocol (MCP) server that exposes only products purchasable through [Stripe Link](https://stripe.com/link). It is designed to be called by a language model, allowing users to view available items and complete a purchase with a single command.

## Features
- Returns only Stripe Link enabled products
- Allows sorting by price, delivery date, or other criteria
- Supports commands like **"buy the xyz one"** to finalize a purchase
- Uses a one-time authorization with Stripe Link for seamless checkout

## Setup
1. Clone the repository
   ```bash
   git clone https://github.com/yourname/link-mcp.git
   cd link-mcp
   ```
2. Install dependencies (Node.js `>=18` or Python `>=3.9` depending on your implementation)
3. Copy `.env.example` to `.env` and fill in your Stripe API keys
4. Start the server
   ```bash
   npm start # or python main.py
   ```

## Usage
1. The LLM queries the MCP server to fetch products. Results are sorted by the criteria provided (for example, by price or delivery date).
2. The user responds with a phrase such as **"buy the xyz one"**, referencing the desired product from the list.
3. The MCP agent completes the transaction via Stripe Link using the stored credentials. The user only needs to authorize into Link once when first using the server.

## Contributing
We welcome contributions!
1. Fork the repository and create a new branch for your feature or fix.
2. Make your changes and add tests if applicable.
3. Run `npm test` or `pytest` to ensure everything passes.
4. Submit a pull request describing your changes.

## License
This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
