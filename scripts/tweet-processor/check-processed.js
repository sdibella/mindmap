#!/usr/bin/env node

/**
 * Check which links have been processed
 * Returns unprocessed links from fetched-tweets.json
 */

const fs = require('fs');
const path = require('path');

const fetchedPath = path.join(__dirname, 'fetched-tweets.json');
const processedPath = path.join(__dirname, '.processed-links.json');

if (!fs.existsSync(fetchedPath)) {
  console.error('No fetched-tweets.json found. Run npm run fetch first.');
  process.exit(1);
}

const fetched = JSON.parse(fs.readFileSync(fetchedPath, 'utf-8'));

let processed = {};
if (fs.existsSync(processedPath)) {
  processed = JSON.parse(fs.readFileSync(processedPath, 'utf-8'));
}

const unprocessed = fetched.filter(tweet => {
  const baseUrl = tweet.url.split('?')[0];
  return !processed[baseUrl] && tweet.accessible;
});

console.log(JSON.stringify(unprocessed, null, 2));
