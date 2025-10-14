const express = require('express');
const { buildSchema } = require('graphql');
const { createHandler } = require('graphql-http/lib/use/express');
const axios = require('axios');
const cors = require('cors');
require('dotenv').config();

const app = express();
const port = process.env.PORT || 4000;
app.use(cors());

// --- GraphQL Schema Definition ---
const schema = buildSchema(`
  """Details for a single item listing from eBay."""
  type ItemDetails {
    title: String!
    imageUrl: String
    currentPrice: Float
    itemWebUrl: String
  }

  """The structured response from an eBay search query."""
  type SearchPayload {
    items: [ItemDetails!]!
    total: Int!
  }

  """The final payload returned to the client, including AI analysis."""
  type MarketAnalysisPayload {
    ebayResults: SearchPayload
    aiAnalysis: String
  }
  
  type Query {
    """A simple query to test if the server is running."""
    hello: String
  }

  type Mutation {
    """Performs a keyword search on eBay and prepares for AI analysis."""
    searchByKeyword(
      query: String!, 
      limit: Int, 
      offset: Int,
      minPrice: Float,
      maxPrice: Float
    ): MarketAnalysisPayload

    """Performs an image-based search on eBay and prepares for AI analysis."""
    searchByImage(
      image: String!,
      limit: Int, 
      offset: Int
    ): MarketAnalysisPayload
  }
`);

// --- eBay API Token Helper Function ---
async function getEbayProdToken() {
  const clientId = process.env.EBAY_PROD_APP_ID;
  const clientSecret = process.env.EBAY_PROD_CERT_ID;

  if (!clientId || !clientSecret) {
    throw new Error('eBay API credentials are not defined in .env file.');
  }

  const tokenUrl = 'https://api.ebay.com/identity/v1/oauth2/token';
  const credentials = Buffer.from(`${clientId}:${clientSecret}`).toString('base64');
  const headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': `Basic ${credentials}`
  };
  const body = new URLSearchParams({
    'grant_type': 'client_credentials',
    'scope': 'https://api.ebay.com/oauth/api_scope'
  });

  try {
    const response = await axios.post(tokenUrl, body.toString(), { headers });
    return response.data.access_token;
  } catch (error) {
    console.error('Error fetching eBay Production Token:', error.response ? error.response.data : error.message);
    throw new Error('Could not fetch eBay Production application token. Check your credentials.');
  }
}

// --- GraphQL Resolvers ---
const root = {
  hello: () => 'Hello from the Sanbi AI Agent API!',

  searchByKeyword: async ({ query, limit = 24, offset = 0, minPrice, maxPrice }) => {
    console.log(`Performing eBay keyword search for: "${query}"`);
    try {
      const accessToken = await getEbayProdToken();
      
      let filterParts = [];
      if (minPrice || maxPrice) {
        filterParts.push(`price:[${minPrice || ''}..${maxPrice || ''}]`);
        filterParts.push(`priceCurrency:USD`);
      }
      const filter = filterParts.join(',');

      const ebayUrl = `https://api.ebay.com/buy/browse/v1/item_summary/search?q=${encodeURIComponent(query)}&limit=${limit}&offset=${offset}&filter=${encodeURIComponent(filter)}`;
      
      const searchResponse = await axios.get(ebayUrl, {
        headers: { 'Authorization': `Bearer ${accessToken}`, 'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US' }
      });

      const itemSummaries = searchResponse.data.itemSummaries || [];
      const items = itemSummaries.map(item => ({
        title: item.title,
        imageUrl: item.image ? item.image.imageUrl : null,
        currentPrice: item.price ? parseFloat(item.price.value) : 0,
        itemWebUrl: item.itemWebUrl,
      }));

      const ebayResults = { items, total: searchResponse.data.total || 0 };

      // --- TODO: AI Analysis Layer ---
      const aiAnalysisResult = "AI analysis is not yet implemented. This section will provide market insights and recommendations.";

      return { ebayResults, aiAnalysis: aiAnalysisResult };
    } catch (error) {
      console.error("eBay Keyword Search Failed:", error.message);
      return {
        ebayResults: { items: [], total: 0 },
        aiAnalysis: "Failed to retrieve data from eBay. Cannot perform analysis. Please check server logs."
      };
    }
  },

  searchByImage: async ({ image, limit = 24, offset = 0 }) => {
    console.log('Performing eBay image search...');
    try {
      const accessToken = await getEbayProdToken();
      const ebayUrl = `https://api.ebay.com/buy/browse/v1/item_summary/search_by_image?limit=${limit}&offset=${offset}`;
      
      const ebayResponse = await axios.post(ebayUrl, { image }, {
        headers: { 'Authorization': `Bearer ${accessToken}`, 'Content-Type': 'application/json', 'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US' }
      });

      const itemSummaries = ebayResponse.data.itemSummaries || [];
      const items = itemSummaries.map(item => ({
        title: item.title,
        imageUrl: item.image ? item.image.imageUrl : null,
        currentPrice: item.price ? parseFloat(item.price.value) : 0,
        itemWebUrl: item.itemWebUrl,
      }));

      const ebayResults = { items, total: ebayResponse.data.total || 0 };

      // --- TODO: AI Analysis Layer ---
      const aiAnalysisResult = "AI analysis is not yet implemented. This section will provide market insights and recommendations.";

      return { ebayResults, aiAnalysis: aiAnalysisResult };
    } catch (error) {
      console.error('eBay Image Search Failed:', error.response ? error.response.data : error.message);
      return {
        ebayResults: { items: [], total: 0 },
        aiAnalysis: "Failed to retrieve data from eBay via image search. Cannot perform analysis."
      };
    }
  },
};

// --- Express Server Setup ---
app.all('/graphql', createHandler({
  schema: schema,
  rootValue: root,
}));

app.listen(port, () => {
  console.log(`Sanbi AI Agent server running at http://localhost:${port}/graphql`);
});