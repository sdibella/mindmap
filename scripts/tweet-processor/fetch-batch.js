#!/usr/bin/env node

/**
 * Fetch tweets in batches
 * Usage: node fetch-batch.js <batch-size> <offset>
 */

const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const { safeReadJSON, fetchTweetContent } = require('./lib/fetch-utils');

const VAULT_PATH = process.env.VAULT_PATH || path.join(process.env.HOME, 'Library/Mobile Documents/iCloud~md~obsidian/Documents/StefanEternal');

// Get batch parameters
const batchSize = parseInt(process.argv[2]) || 20;
const offset = parseInt(process.argv[3]) || 0;

/**
 * Load bookmarked tweet URLs
 */
function loadBookmarkedLinks() {
  const bookmarksPath = path.join(__dirname, 'bookmarked-urls.json');
  const bookmarks = safeReadJSON(bookmarksPath, []);
  return bookmarks.map(b => ({
    url: b.url,
    baseUrl: b.baseUrl,
    files: ['bookmarks'],
    firstSeen: 'bookmarks'
  }));
}

async function main() {
  console.log(`🔗 Batch Fetcher - Processing ${batchSize} tweets (offset: ${offset})\n`);

  // Load all bookmarks
  const allLinks = loadBookmarkedLinks();

  // Load processed links
  const processedFile = path.join(__dirname, '.processed-links.json');
  let processed = safeReadJSON(processedFile, {});

  // Filter to unprocessed only
  const unprocessedLinks = allLinks.filter(link => !processed[link.baseUrl]);

  console.log(`Total bookmarks: ${allLinks.length}`);
  console.log(`Already processed: ${allLinks.length - unprocessedLinks.length}`);
  console.log(`Remaining: ${unprocessedLinks.length}`);

  // Get this batch
  const batchLinks = unprocessedLinks.slice(offset, offset + batchSize);

  if (batchLinks.length === 0) {
    console.log('\n✅ No more tweets to process!');
    return;
  }

  console.log(`\nProcessing batch: ${offset + 1} to ${offset + batchLinks.length}\n`);

  // Load cookies
  const cookiesPath = path.join(__dirname, '.cookies.json');
  const cookies = safeReadJSON(cookiesPath, null);

  // Launch browser
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });

  if (cookies) {
    await context.addCookies(cookies);
  }

  // Fetch tweets
  const results = [];
  let fetched = 0;
  let failed = 0;

  for (let i = 0; i < batchLinks.length; i++) {
    const link = batchLinks[i];
    console.log(`[${i + 1}/${batchLinks.length}] ${link.baseUrl}`);

    const result = await fetchTweetContent(context, link.url);
    result.foundIn = link.files;
    result.firstSeen = link.firstSeen;

    if (result.accessible) {
      console.log('  ✓ Success');
      fetched++;
    } else {
      console.log(`  ✗ Failed: ${result.error || 'Unknown'}`);
      failed++;
    }

    results.push(result);
    await new Promise(resolve => setTimeout(resolve, 2000));
  }

  await context.close();
  await browser.close();

  // Append to fetched-tweets.json (with deduplication)
  const fetchedPath = path.join(__dirname, 'fetched-tweets.json');
  let allFetched = safeReadJSON(fetchedPath, []);
  const existingUrls = new Set(allFetched.map(r => r.url));

  for (const result of results) {
    if (!existingUrls.has(result.url)) {
      allFetched.push(result);
    }
  }
  fs.writeFileSync(fetchedPath, JSON.stringify(allFetched, null, 2));

  console.log('\n================================');
  console.log(`✓ Fetched: ${fetched}`);
  console.log(`✗ Failed: ${failed}`);
  console.log(`Success Rate: ${((fetched / batchLinks.length) * 100).toFixed(1)}%`);
  console.log('================================\n');
  console.log(`Batch saved to fetched-tweets.json`);
  console.log(`Ready to process with Claude Code!`);
}

main().catch(console.error);
