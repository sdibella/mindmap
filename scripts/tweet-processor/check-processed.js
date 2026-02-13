#!/usr/bin/env node

/**
 * Check which links have been processed
 * Returns unprocessed links from fetched-tweets.json
 */

const fs = require('fs');
const path = require('path');
const { safeReadJSON } = require('./lib/fetch-utils');

const fetchedPath = path.join(__dirname, 'fetched-tweets.json');
const processedPath = path.join(__dirname, '.processed-links.json');

const fetched = safeReadJSON(fetchedPath, null);
if (!fetched) {
  console.error('No fetched-tweets.json found. Run npm run fetch first.');
  process.exit(1);
}

const processed = safeReadJSON(processedPath, {});

const unprocessed = fetched.filter(tweet => {
  const baseUrl = tweet.url.split('?')[0];
  return !processed[baseUrl] && tweet.accessible;
});

console.log(JSON.stringify(unprocessed, null, 2));
