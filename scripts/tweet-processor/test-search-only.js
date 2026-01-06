#!/usr/bin/env node

/**
 * Simple test for Google Custom Search Engine (no AI needed)
 */

const https = require('https');
require('dotenv').config();

const searchEngineId = process.env.GOOGLE_SEARCH_ENGINE_ID;
const googleApiKey = process.env.GOOGLE_API_KEY;

async function testSearch(query) {
  console.log(`🔍 Testing Google Custom Search Engine...`);
  console.log(`Search Engine ID: ${searchEngineId}`);
  console.log(`Query: "${query}"\n`);

  return new Promise((resolve) => {
    const encodedQuery = encodeURIComponent(query);
    const url = `https://www.googleapis.com/customsearch/v1?key=${googleApiKey}&cx=${searchEngineId}&q=${encodedQuery}&num=3`;

    https.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const results = JSON.parse(data);

          if (results.error) {
            console.log(`❌ Search API Error:`);
            console.log(`   Code: ${results.error.code}`);
            console.log(`   Message: ${results.error.message}`);
            console.log(`\n💡 Check: https://console.cloud.google.com/apis/credentials`);
            resolve(false);
            return;
          }

          if (results.items) {
            console.log(`✅ Search successful! Found ${results.items.length} results:\n`);
            results.items.forEach((item, i) => {
              console.log(`${i + 1}. ${item.title}`);
              console.log(`   ${item.link}`);
              console.log(`   ${item.snippet}\n`);
            });
            resolve(true);
          } else {
            console.log(`⚠️  No results found for this query`);
            resolve(true);
          }
        } catch (e) {
          console.log(`❌ Parse error: ${e.message}`);
          resolve(false);
        }
      });
    }).on('error', (e) => {
      console.log(`❌ Network error: ${e.message}`);
      resolve(false);
    });
  });
}

async function main() {
  console.log('🧪 Google Custom Search Engine Test');
  console.log('================================\n');

  const testQuery = "RAG systems Claude API";
  const success = await testSearch(testQuery);

  console.log('================================');
  if (success) {
    console.log('✅ Auto-research search functionality is working!');
    console.log('\n📝 Note: Full AI filtering test requires API quota.');
    console.log('   When you process real tweets, the full pipeline will:');
    console.log('   1. Generate optimal search query with AI');
    console.log('   2. Search web (just tested ✅)');
    console.log('   3. Filter/rank results with AI');
  } else {
    console.log('❌ Search engine setup needs attention.');
  }
}

main();
