#!/usr/bin/env node

/**
 * Test script for auto-research feature
 */

const { GoogleGenerativeAI } = require('@google/generative-ai');
const https = require('https');
require('dotenv').config();

const CONFIG = {
  maxResearchResults: parseInt(process.env.MAX_RESEARCH_RESULTS) || 5,
  researchRelevanceThreshold: parseFloat(process.env.RESEARCH_RELEVANCE_THRESHOLD) || 0.6,
  googleApiKey: process.env.GOOGLE_API_KEY,
  searchEngineId: process.env.GOOGLE_SEARCH_ENGINE_ID
};

const genAI = new GoogleGenerativeAI(CONFIG.googleApiKey);
const aiClient = genAI.getGenerativeModel({ model: 'gemini-3-flash-preview' });

// Sample tweet data for testing
const testTweetData = {
  text: "Just shipped a RAG system using Claude's 200K context window. Game changer for technical documentation search. No more chunking headaches!",
  tags: ["ai", "rag", "claude", "llm"],
  category: "resource",
  author: "@swyx",
  authorName: "Shawn Wang"
};

async function generateSearchQuery(tweetData) {
  console.log(`\n🔍 Generating search query...`);

  const prompt = `Based on this tweet, generate an optimal web search query to find related articles, tutorials, and resources.

Tweet content: "${tweetData.text}"
Tags: ${tweetData.tags.join(', ')}
Category: ${tweetData.category}

Generate a concise search query (3-7 words) that will find the most relevant technical resources.
Respond with ONLY the search query text, nothing else.`;

  const result = await aiClient.generateContent(prompt);
  const response = await result.response;
  const searchQuery = response.text().trim().replace(/['"]/g, '');

  console.log(`✓ Search query: "${searchQuery}"`);
  return searchQuery;
}

async function performWebSearch(query) {
  console.log(`\n🌐 Searching the web...`);

  return new Promise((resolve, reject) => {
    const encodedQuery = encodeURIComponent(query);
    const url = `https://www.googleapis.com/customsearch/v1?key=${CONFIG.googleApiKey}&cx=${CONFIG.searchEngineId}&q=${encodedQuery}&num=${CONFIG.maxResearchResults}`;

    https.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const results = JSON.parse(data);
          if (results.error) {
            console.log(`✗ Search error: ${results.error.message}`);
            resolve([]);
            return;
          }
          if (results.items) {
            console.log(`✓ Found ${results.items.length} results`);
            resolve(results.items.map(item => ({
              title: item.title,
              url: item.link,
              snippet: item.snippet
            })));
          } else {
            console.log(`⚠️  No search results found`);
            resolve([]);
          }
        } catch (e) {
          console.log(`✗ Parse error: ${e.message}`);
          resolve([]);
        }
      });
    }).on('error', (e) => {
      console.log(`✗ Network error: ${e.message}`);
      resolve([]);
    });
  });
}

async function filterResearchResults(searchResults, tweetData) {
  if (searchResults.length === 0) return [];

  console.log(`\n🤖 Filtering results with AI...`);

  const prompt = `You are filtering web search results to find the most relevant resources for a software engineer.

Tweet content: "${tweetData.text}"
User interests: AI/LLM projects, knowledge management, web development
Tags: ${tweetData.tags.join(', ')}

Search results:
${searchResults.map((r, i) => `${i + 1}. ${r.title}\n   ${r.snippet}\n   ${r.url}`).join('\n\n')}

For each result, assign a relevance score (0.0-1.0) and brief explanation.
Return ONLY valid JSON (no markdown, no code blocks):

{
  "results": [
    {
      "index": 1,
      "relevance": 0.95,
      "reason": "why this is relevant",
      "summary": "one-sentence summary of what this resource offers"
    }
  ]
}

Only include results with relevance >= ${CONFIG.researchRelevanceThreshold}.
Prioritize: technical depth, actionable insights, credible sources.`;

  const result = await aiClient.generateContent(prompt);
  const response = await result.response;
  let jsonText = response.text().trim();

  if (jsonText.startsWith('```')) {
    jsonText = jsonText.replace(/```json?\n?/g, '').replace(/```\n?$/g, '');
  }

  const filtered = JSON.parse(jsonText);

  const enrichedResults = filtered.results
    .filter(r => r.relevance >= CONFIG.researchRelevanceThreshold)
    .map(r => ({
      ...searchResults[r.index - 1],
      relevance: r.relevance,
      reason: r.reason,
      summary: r.summary
    }))
    .sort((a, b) => b.relevance - a.relevance);

  console.log(`✓ Filtered to ${enrichedResults.length} relevant results`);
  return enrichedResults;
}

async function main() {
  console.log('🧪 Auto-Research Feature Test');
  console.log('================================\n');
  console.log(`Testing with sample tweet:`);
  console.log(`"${testTweetData.text}"\n`);
  console.log(`Tags: ${testTweetData.tags.join(', ')}`);
  console.log(`Category: ${testTweetData.category}`);

  try {
    // Step 1: Generate search query
    const searchQuery = await generateSearchQuery(testTweetData);

    // Step 2: Search the web
    const searchResults = await performWebSearch(searchQuery);

    if (searchResults.length === 0) {
      console.log('\n❌ No search results found. Check your API configuration.');
      return;
    }

    // Step 3: Filter and rank
    const filteredResults = await filterResearchResults(searchResults, testTweetData);

    // Step 4: Display results
    console.log('\n📊 Final Research Results:');
    console.log('================================\n');
    console.log(`Search Query: "${searchQuery}"\n`);

    if (filteredResults.length === 0) {
      console.log('No results met the relevance threshold.');
    } else {
      filteredResults.forEach((result, idx) => {
        const relevanceLabel = result.relevance >= 0.8 ? 'High' : result.relevance >= 0.6 ? 'Medium' : 'Low';
        console.log(`${idx + 1}. ${result.title}`);
        console.log(`   URL: ${result.url}`);
        console.log(`   Summary: ${result.summary || result.snippet}`);
        console.log(`   Relevance: ${relevanceLabel} (${(result.relevance * 100).toFixed(0)}%)`);
        if (result.reason) {
          console.log(`   Why: ${result.reason}`);
        }
        console.log('');
      });
    }

    console.log('================================');
    console.log('✅ Auto-research test completed successfully!');

  } catch (error) {
    console.error('\n❌ Test failed:', error.message);
    console.error(error.stack);
  }
}

main();
