const axios = require('axios');

module.exports = {
  name: 'stripe-filter',
  description: 'Filter a list of products to only those using Stripe for payments',
  inputSchema: {
    type: 'object',
    properties: {
      products: {
        type: 'array',
        description: 'List of products to filter',
        items: {
          type: 'object',
          properties: {
            url: {
              type: 'string',
              description: 'Product URL'
            },
            name: {
              type: 'string',
              description: 'Product name'
            }
          },
          required: ['url']
        }
      }
    },
    required: ['products']
  },
  async handler({ products }) {
    try {
      const response = await axios.post('http://localhost:5000/api/filter-products', {
        products
      });
      return response.data;
    } catch (error) {
      return {
        products: [],
        error: error.message
      };
    }
  }
};