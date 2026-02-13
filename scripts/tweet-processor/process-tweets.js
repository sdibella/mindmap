#!/usr/bin/env node

/**
 * Fetch and validate tweets for review
 * Dumb ingestion layer - no categorization
 * openclaw agent handles review, categorization, and atomization
 */

const fs = require('fs');
const path = require('path');
const { safeReadJSON } = require('./lib/fetch-utils');

const SCRIPT_DIR = __dirname;
const FETCHED_PATH = path.join(SCRIPT_DIR, 'fetched-tweets.json');
const REVIEW_QUEUE_PATH = path.join(SCRIPT_DIR, 'review-queue.json');

/**
 * Main - fetch valid tweets and add to review queue
 */
async function main() {
  console.log('📥 Fetching tweets for review...\n');

  // Load fetched tweets
  const tweets = safeReadJSON(FETCHED_PATH, []);
  if (tweets.length === 0) {
    console.error('No fetched-tweets.json found or file is empty.');
    process.exit(1);
  }

  // Load review queue
  let reviewQueue = safeReadJSON(REVIEW_QUEUE_PATH, []);
  const queuedUrls = new Set(reviewQueue.map(t => t.url));

  // Filter for valid new tweets
  const validTweets = tweets.filter(t => {
    const baseUrl = t.url.split('?')[0];
    return t.accessible &&
      t.content &&
      t.content.length > 50 &&
      !t.url.includes('/analytics') &&
      !t.url.includes('/photo/') &&
      !t.url.includes('/media_tags') &&
      !queuedUrls.has(baseUrl);
  });

  console.log(`Found ${validTweets.length} new tweets\n`);

  if (validTweets.length === 0) {
    console.log('No new tweets to add to review queue.');
    return;
  }

  // Add to review queue
  for (const tweet of validTweets) {
    reviewQueue.push({
      url: tweet.url.split('?')[0],
      author: tweet.author,
      handle: tweet.handle,
      content: tweet.content,
      source: tweet.firstSeen,
      addedAt: new Date().toISOString(),
      reviewed: false
    });
  }

  // Save review queue
  fs.writeFileSync(REVIEW_QUEUE_PATH, JSON.stringify(reviewQueue, null, 2));

  console.log('================================');
  console.log(`✓ Added to review: ${validTweets.length}`);
  console.log(`📋 Total in queue: ${reviewQueue.length}`);
  console.log('================================\n');
  console.log(`Ready for openclaw to process.`);
}

/**
 * Deduplication utility - fixes stuck tweets in loop
 * Run with: node process-tweets.js --dedup
 *
 * Checks for atom files that exist but aren't marked as processed,
 * then marks them in .processed-links.json to prevent re-detection
 */
async function dedupMode() {
  const VAULT_PATH = process.env.VAULT_PATH || '/Volumes/My Shared Files/StefanEternal';
  const ATOMS_PATH = path.join(VAULT_PATH, 'atoms');
  const PROCESSED_FILE = path.join(SCRIPT_DIR, '.processed-links.json');

  if (!fs.existsSync(ATOMS_PATH)) {
    console.error(`❌ Atoms directory not found: ${ATOMS_PATH}`);
    process.exit(1);
  }

  console.log('🔍 Scanning for stuck tweets...\n');

  const atomFiles = fs.readdirSync(ATOMS_PATH).filter(f => f.endsWith('.md'));
  let processed = safeReadJSON(PROCESSED_FILE, {});
  let fixed = 0;

  for (const file of atomFiles) {
    const filePath = path.join(ATOMS_PATH, file);
    const content = fs.readFileSync(filePath, 'utf-8');

    // Extract source URL from frontmatter
    const match = content.match(/source: (https:\/\/[^\n]+)/);
    if (!match) continue;

    const sourceUrl = match[1].trim();

    // If atom exists but URL not in processed list, add it
    if (!processed[sourceUrl]) {
      processed[sourceUrl] = {
        processedAt: new Date().toISOString(),
        url: sourceUrl,
        deduped: true
      };
      console.log(`✓ Fixed: ${sourceUrl}`);
      fixed++;
    }
  }

  if (fixed > 0) {
    fs.writeFileSync(PROCESSED_FILE, JSON.stringify(processed, null, 2));
    console.log(`\n================================`);
    console.log(`✓ Deduped: ${fixed} stuck tweets`);
    console.log(`================================\n`);
  } else {
    console.log('✓ No stuck tweets found\n');
  }
}

// Handle CLI args
if (process.argv[2] === '--dedup') {
  dedupMode().catch(console.error);
} else {
  main().catch(console.error);
}
