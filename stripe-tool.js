const axios = require('axios');

module.exports = {
  name: 'stripe-detector',
  description: 'Detect if a website or product uses Stripe for payments',
  inputSchema: {
    type: 'object',
    properties: {
      url: {
        type: 'string',
        description: 'The URL to check for Stripe integration'
      }
    },
    required: ['url']
  },
  async handler({ url }) {
    try {
      const response = await axios.post('http://localhost:5000/api/validate-url', {
        url
      });
      return response.data;
    } catch (error) {
      return {
        stripe_enabled: false,
        confidence: 0,
        error: error.message
      };
    }
  }
};