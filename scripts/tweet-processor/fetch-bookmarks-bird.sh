#!/bin/bash
# X Bookmark Fetcher using bird CLI
# Faster, lightweight alternative to Playwright

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export VAULT_PATH="${VAULT_PATH:-/Volumes/My Shared Files/StefanEternal}"
LOG_FILE="${HOME}/.x-bookmark-fetch.log"
RAW_FILE="${SCRIPT_DIR}/.bird-bookmarks-raw.json"
OUTPUT_FILE="${SCRIPT_DIR}/bookmarked-urls.json"

echo "🔖 X Bookmark Fetcher (bird CLI)" | tee -a "$LOG_FILE"
echo "================================" | tee -a "$LOG_FILE"
date | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Use bird to fetch bookmarks (up to 100)
echo "📚 Fetching bookmarks via bird..." | tee -a "$LOG_FILE"

# Fetch bookmarks as JSON and transform to expected format
if ! bird bookmarks --all --json > "${RAW_FILE}" 2>> "$LOG_FILE"; then
    echo "❌ Failed to fetch bookmarks via bird" | tee -a "$LOG_FILE"
    echo "Check: 1) Chrome is logged into X" | tee -a "$LOG_FILE"
    echo "       2) bird CLI is installed: npm list -g @steipete/bird" | tee -a "$LOG_FILE"
    exit 1
fi

# Transform bird output to bookmarked-urls.json format
echo "🔄 Transforming output..." | tee -a "$LOG_FILE"

# Use node.js to transform the output
SCRIPT_DIR="${SCRIPT_DIR}" node -e "
const fs = require('fs');
const path = require('path');

const scriptDir = process.env.SCRIPT_DIR;
const rawPath = path.join(scriptDir, '.bird-bookmarks-raw.json');
const outputPath = path.join(scriptDir, 'bookmarked-urls.json');

if (!fs.existsSync(rawPath)) {
    console.error('No raw bookmarks file found');
    process.exit(1);
}

const rawData = JSON.parse(fs.readFileSync(rawPath, 'utf-8'));

// Handle both { tweets: [...] } and [...] formats
const tweets = rawData.tweets || (Array.isArray(rawData) ? rawData : []);

if (tweets.length === 0) {
    console.log('No bookmarks found');
    fs.writeFileSync(outputPath, JSON.stringify([], null, 2));
    fs.unlinkSync(rawPath);
    process.exit(0);
}

// Transform bird output to expected format
const bookmarks = tweets.map(tweet => {
    const handle = tweet.author && (tweet.author.username || tweet.author.handle || tweet.author.name);
    if (!handle) {
        console.error('Skipping tweet with no author:', JSON.stringify(tweet).slice(0, 100));
        return null;
    }
    const baseUrl = 'https://x.com/' + handle + '/status/' + tweet.id;
    return {
        url: baseUrl,
        baseUrl: baseUrl,
        fetchedAt: new Date().toISOString(),
        birdData: {
            id: tweet.id,
            author: tweet.author.name,
            handle: handle,
            text: tweet.text,
            createdAt: tweet.createdAt,
            metrics: {
                replies: tweet.replyCount,
                retweets: tweet.retweetCount,
                likes: tweet.likeCount
            },
            media: tweet.media || []
        }
    };
}).filter(b => b !== null);

fs.writeFileSync(outputPath, JSON.stringify(bookmarks, null, 2));
console.log('✓ Saved ' + bookmarks.length + ' bookmarks');

// Merge into fetched-tweets.json (dedup by URL)
const fetchedPath = path.join(scriptDir, 'fetched-tweets.json');
let existing = [];
try { existing = JSON.parse(fs.readFileSync(fetchedPath, 'utf-8')); } catch (e) {}
const existingUrls = new Set(existing.map(r => r.url));

let added = 0;
for (const b of bookmarks) {
    if (!existingUrls.has(b.baseUrl) && b.birdData.text) {
        existing.push({
            url: b.baseUrl,
            accessible: true,
            content: b.birdData.text,
            author: b.birdData.author,
            handle: b.birdData.handle,
            createdAt: b.birdData.createdAt,
            metrics: b.birdData.metrics,
            media: b.birdData.media,
            timestamp: new Date().toISOString(),
            foundIn: ['bookmarks'],
            firstSeen: 'bookmarks'
        });
        added++;
    }
}

fs.writeFileSync(fetchedPath, JSON.stringify(existing, null, 2));
console.log('✓ Merged ' + added + ' new tweets into fetched-tweets.json (' + existing.length + ' total)');

// Clean up raw file
fs.unlinkSync(rawPath);
" | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "✓ Bookmarks fetched and merged" | tee -a "$LOG_FILE"
echo "================================" | tee -a "$LOG_FILE"
date | tee -a "$LOG_FILE"
