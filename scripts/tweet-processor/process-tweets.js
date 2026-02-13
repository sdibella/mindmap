#!/usr/bin/env node

/**
 * Process fetched tweets into vault - Atomic Note Format
 * Updated for StefanEternal AI-native structure
 */

const fs = require('fs');
const path = require('path');
const { safeReadJSON } = require('./lib/fetch-utils');

const VAULT_PATH = process.env.VAULT_PATH || '/Volumes/My Shared Files/StefanEternal';
const ATOMS_PATH = path.join(VAULT_PATH, 'atoms');
const MAPS_PATH = path.join(VAULT_PATH, 'maps');
const LOGS_PATH = path.join(VAULT_PATH, 'logs/discoveries');

/**
 * Generate a slug from tweet content
 */
function generateSlug(content) {
  // Extract first meaningful sentence or key phrases
  const lines = content.split('\n').filter(l => l.trim().length > 10);
  let text = lines[0] || content;

  // Clean up common tweet artifacts
  text = text.replace(/^.*?@\w+/, ''); // Remove username
  text = text.replace(/Subscribe/gi, '');
  text = text.replace(/\d+\s*$/g, ''); // Remove trailing numbers

  // Take first meaningful phrase
  text = text.substring(0, 80).trim();

  // Convert to slug
  const slug = text
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')
    .substring(0, 60);

  return slug || 'tweet-' + Date.now();
}

/**
 * Generate title from content
 */
function generateTitle(content) {
  const lines = content.split('\n').filter(l => l.trim().length > 10);
  let title = lines[0] || content;

  // Clean up
  title = title.replace(/^.*?@\w+/, '').trim();
  title = title.replace(/Subscribe/gi, '').trim();
  title = title.replace(/\d+\s*$/g, '').trim();

  // Capitalize first letter
  title = title.charAt(0).toUpperCase() + title.slice(1);

  // Truncate if too long
  if (title.length > 80) {
    title = title.substring(0, 77) + '...';
  }

  return title || 'Tweet';
}

/**
 * Extract tags from content
 */
function extractTags(content) {
  const tags = ['tweet', 'migrated'];
  
  // Keyword detection with word boundaries where needed
  if (/agent/i.test(content) || /\bai\b/i.test(content)) tags.push('ai-agents');
  if (/trading/i.test(content) || /\bmarket\b/i.test(content)) tags.push('trading');
  if (/\bcode\b/i.test(content) || /programming/i.test(content)) tags.push('development');
  if (/business/i.test(content) || /startup/i.test(content)) tags.push('business');
  
  return tags;
}

/**
 * Process a single tweet as atomic note
 */
function processTweet(tweet) {
  const baseUrl = tweet.url.split('?')[0];
  const slug = generateSlug(tweet.content);
  const title = generateTitle(tweet.content);
  const today = new Date().toISOString().split('T')[0];
  const tags = extractTags(tweet.content);
  
  // Extract author from URL
  const authorMatch = baseUrl.match(/x\.com\/([^\/]+)\/status/);
  const author = authorMatch ? authorMatch[1] : 'unknown';

  const markdown = `---
tags: [${tags.join(', ')}]
created: ${today}
updated: ${today}
source: ${baseUrl}
author: @${author}
type: tweet
---

# ${title}

## Content

${tweet.content.length > 2000 ? tweet.content.substring(0, 2000) + '...' : tweet.content}

## Source
- [Original Tweet](${baseUrl})
- Author: @${author}

## Key Takeaways

- 

## Related Atoms
- [[ai-native-knowledge-base]]
- [[atomic-note]]

## See Also
- [[maps/ai-agents]] — AI-related topics
- [[maps/investment]] — Trading and markets
`;

  // Write file
  const filename = `${slug}.md`;
  const filepath = path.join(ATOMS_PATH, filename);

  // Check if file already exists
  if (fs.existsSync(filepath)) {
    console.log(`  ⚠️  File already exists: ${filename}`);
    return null;
  }

  fs.writeFileSync(filepath, markdown);
  return { filename, slug, tags };
}

/**
 * Update X Bookmarks index
 */
function updateXBookmarksIndex(processed) {
  const today = new Date().toISOString().split('T')[0];

  // Build entries from processed data
  const entries = Object.entries(processed)
    .map(([url, data]) => {
      const match = url.match(/x\.com\/([^\/]+)\/status\/(\d+)/);
      if (!match) return null;
      return {
        author: match[1],
        statusId: match[2],
        url: url,
        date: data.processedAt ? data.processedAt.split('T')[0] : 'unknown'
      };
    })
    .filter(e => e !== null)
    .sort((a, b) => b.date.localeCompare(a.date));

  let indexMarkdown = `---
tags: [index, bookmarks, x]
created: 2026-02-02
updated: ${today}
---

# X Bookmarks

Master index of all bookmarked tweets processed into the vault as atomic notes.

## Stats

- **Total processed:** ${entries.length}
- **Format:** Atomic notes in \`atoms/\`
- **Last updated:** ${today}

## All Processed Tweets

| Date | Author | Atom |
|------|--------|------|
`;

  entries.forEach(e => {
    indexMarkdown += `| ${e.date} | @${e.author} | [[${e.statusId}-${e.author}]] |\n`;
  });

  indexMarkdown += `
---

*This index is updated each time new bookmarks are processed.*
*Notes are stored as atomic format in \`atoms/\` folder.*
`;

  const indexPath = path.join(MAPS_PATH, 'x-bookmarks.md');
  fs.writeFileSync(indexPath, indexMarkdown);
  console.log(`📋 Updated maps/x-bookmarks.md (${entries.length} total)`);
}

/**
 * Create discovery log entry for batch
 */
function createDiscoveryLog(processed, count) {
  const today = new Date().toISOString().split('T')[0];
  const logFilename = `x-bookmarks-${today}.md`;
  const logPath = path.join(LOGS_PATH, logFilename);

  const recent = Object.entries(processed)
    .slice(-5)
    .map(([url, data]) => {
      const match = url.match(/x\.com\/([^\/]+)\/status\/(\d+)/);
      return match ? `- [[${match[2]}-${match[1]}]]` : null;
    })
    .filter(Boolean)
    .join('\n');

  let logMarkdown = `---
tags: [log, discovery, bookmarks]
created: ${today}
importance: medium
---

# Discovery: X Bookmarks Batch

## Summary
Processed ${count} new tweets from bookmarks into atomic notes.

## New Atoms
${recent}

## Notes
- Automated fetch via cron job (midnight/noon)
- Processed using atomic note format
- Check [[maps/x-bookmarks]] for full index

## Next Steps
- [ ] Review new atoms in \`atoms/\`
- [ ] Link to relevant MOCs
`;

  fs.writeFileSync(logPath, logMarkdown);
  console.log(`📝 Created discovery log: ${logFilename}`);
}

/**
 * Main
 */
async function main() {
  const batchSize = parseInt(process.argv[2]) || 10;

  console.log('📝 Processing tweets into vault (atomic format)...\n');

  // Load tweets
  const tweets = safeReadJSON(path.join(__dirname, 'fetched-tweets.json'), []);
  if (tweets.length === 0) {
    console.error('No fetched-tweets.json found or file is empty.');
    return;
  }

  // Load processed
  const processedFile = path.join(__dirname, '.processed-links.json');
  let processed = safeReadJSON(processedFile, {});

  // Filter for valid new tweets
  const validTweets = tweets.filter(t => {
    const baseUrl = t.url.split('?')[0];
    return t.accessible &&
      t.content &&
      t.content.length > 50 &&
      !t.url.includes('/analytics') &&
      !t.url.includes('/photo/') &&
      !t.url.includes('/media_tags') &&
      !processed[baseUrl];
  });

  console.log(`Found ${validTweets.length} new tweets to process`);
  console.log(`Processing first ${Math.min(batchSize, validTweets.length)}...\n`);

  // Process batch
  let successCount = 0;
  let skipCount = 0;
  const newAtoms = [];

  for (let i = 0; i < Math.min(batchSize, validTweets.length); i++) {
    const tweet = validTweets[i];
    const baseUrl = tweet.url.split('?')[0];

    console.log(`[${i + 1}/${Math.min(batchSize, validTweets.length)}] ${baseUrl}`);

    const result = processTweet(tweet);
    if (result) {
      console.log(`  ✓ Created: ${result.filename}`);
      console.log(`     Tags: ${result.tags.join(', ')}`);

      // Mark as processed
      processed[baseUrl] = {
        processedAt: new Date().toISOString(),
        url: baseUrl
      };

      successCount++;
      newAtoms.push(result.filename);
    } else {
      skipCount++;
    }
  }

  // Save processed links
  fs.writeFileSync(processedFile, JSON.stringify(processed, null, 2));

  // Update indexes
  if (successCount > 0) {
    updateXBookmarksIndex(processed);
    createDiscoveryLog(processed, successCount);
  }

  console.log('\n================================');
  console.log(`✓ Processed: ${successCount}`);
  console.log(`⚠️  Skipped: ${skipCount}`);
  console.log(`📁 Location: atoms/`);
  console.log('================================\n');
  console.log(`Remaining to process: ${validTweets.length - batchSize}`);
}

main().catch(console.error);
