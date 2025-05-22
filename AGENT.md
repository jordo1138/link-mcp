# Link MCP Agent Guidelines

## Commands
- Run server: `python server.py`
- Install dependencies: `pip install -r requirements.txt`
- Run all tests: `python pytest.py`
- Run a single test: `python -m pytest tests/test_file.py::test_function -v`
- Set environment variable: `export STRIPE_API_KEY=your_key_here`

## Code Style
- Use type hints for function parameters and return values
- Follow PEP 8 naming conventions (snake_case for variables/functions)
- Import order: standard library → third-party → local modules
- Use docstrings for functions ("""triple quotes""")
- Error handling: check conditions early and return/raise appropriately
- JSON response format: use jsonify() for Flask responses
- Environment variables for configuration
- Use relative imports within the app package

## Structure
- Flask blueprints for route organization
- Separate services for business logic
- Store data in JSON files under data/ directory