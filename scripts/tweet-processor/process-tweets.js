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

main().catch(console.error);
