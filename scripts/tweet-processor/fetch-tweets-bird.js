#!/usr/bin/env node
/**
 * Tweet Fetcher using bird CLI
 * Fast, lightweight alternative to Playwright
 */
const fs = require('fs');
const path = require('path');
const { execSync, execFileSync } = require('child_process');
const { safeReadJSON } = require('./lib/fetch-utils');

const SCRIPT_DIR = __dirname;

/**
 * Execute bird command and return JSON output
 */
function birdRead(url) {
  try {
    const output = execFileSync('bird', [url, '--json'], {
      encoding: 'utf-8',
      timeout: 30000,
      cwd: SCRIPT_DIR
    });
    return JSON.parse(output);
  } catch (error) {
    console.error(`✗ Failed to fetch ${url}: ${error.message}`);
    return null;
  }
}

/**
 * Main function
 */
async function main() {
  console.log('🔗 X Tweet Fetcher (bird CLI)\n');
  
  // Load bookmarked URLs
  const bookmarksPath = path.join(SCRIPT_DIR, 'bookmarked-urls.json');
  if (!fs.existsSync(bookmarksPath)) {
    console.error('❌ No bookmarked-urls.json found');
    console.error('   Run: fetch-bookmarks-bird.sh first\n');
    process.exit(1);
  }
  
  const bookmarks = safeReadJSON(bookmarksPath, []);
  console.log(`Found ${bookmarks.length} bookmarked tweet(s)\n`);
  
  if (bookmarks.length === 0) {
    console.log('No links to fetch.');
    return;
  }
  
  // Check bird is installed
  try {
    execSync('bird --version', { encoding: 'utf-8' });
  } catch (e) {
    console.error('❌ bird CLI not found');
    console.error('   Install: npm i -g @steipete/bird\n');
    process.exit(1);
  }
  
  // Load existing fetched tweets to avoid re-fetching
  const fetchedPath = path.join(SCRIPT_DIR, 'fetched-tweets.json');
  let existingResults = [];
  const fetchedUrls = new Set();
  
  if (fs.existsSync(fetchedPath)) {
    existingResults = safeReadJSON(fetchedPath, []);
    existingResults.forEach(r => {
      if (r.accessible) fetchedUrls.add(r.url);
    });
    console.log(`ℹ️  ${fetchedUrls.size} tweets already cached\n`);
  }
  
  // Fetch tweets
  const results = [...existingResults];
  let fetched = 0;
  let skipped = 0;
  let failed = 0;
  
  for (const bookmark of bookmarks) {
    const url = bookmark.baseUrl;
    
    // Skip if already fetched
    if (fetchedUrls.has(url)) {
      console.log(`⏩ Skipping (cached): ${url}`);
      skipped++;
      continue;
    }
    
    console.log(`Fetching: ${url}`);
    const tweet = birdRead(url);
    
    if (tweet) {
      const result = {
        url: url,
        accessible: true,
        content: tweet.text,
        author: tweet.author.name,
        handle: tweet.author.handle,
        createdAt: tweet.createdAt,
        metrics: tweet.metrics,
        media: tweet.media || [],
        timestamp: new Date().toISOString(),
        foundIn: ['bookmarks'],
        firstSeen: 'bookmarks'
      };
      results.push(result);
      console.log(' ✓ Success');
      fetched++;
      
      // Rate limiting: gentle delay
      await new Promise(resolve => setTimeout(resolve, 500));
    } else {
      results.push({
        url: url,
        accessible: false,
        error: 'Failed to fetch via bird',
        timestamp: new Date().toISOString(),
        foundIn: ['bookmarks'],
        firstSeen: 'bookmarks'
      });
      failed++;
    }
  }
  
  // Save results
  fs.writeFileSync(fetchedPath, JSON.stringify(results, null, 2));
  
  console.log('\n================================');
  console.log(`✓ Fetched: ${fetched}`);
  console.log(`⏩ Skipped: ${skipped}`);
  console.log(`✗ Failed: ${failed}`);
  console.log(`Total: ${results.length}`);
  console.log('================================\n');
  console.log(`Results saved to: fetched-tweets.json`);
}

main().catch(console.error);
