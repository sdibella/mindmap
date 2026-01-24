#!/usr/bin/env node

/**
 * Mark a URL as processed
 * Usage: node mark-processed.js <url>
 */

const fs = require('fs');
const path = require('path');

const url = process.argv[2];

if (!url) {
  console.error('Usage: node mark-processed.js <url>');
  process.exit(1);
}

const processedPath = path.join(__dirname, '.processed-links.json');

let processed = {};
if (fs.existsSync(processedPath)) {
  processed = JSON.parse(fs.readFileSync(processedPath, 'utf-8'));
}

const baseUrl = url.split('?')[0];
processed[baseUrl] = {
  processedAt: new Date().toISOString(),
  url: url
};

fs.writeFileSync(processedPath, JSON.stringify(processed, null, 2));
console.log(`Marked as processed: ${baseUrl}`);
