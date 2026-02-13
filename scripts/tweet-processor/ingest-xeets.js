#!/usr/bin/env node
/**
 * Ingest Xeets to Review into fetched-tweets.json
 * Dumb ingestion: just extract, deduplicate, and store
 * No categorization or intelligence
 */

const fs = require('fs');
const path = require('path');
const { safeReadJSON } = require('./lib/fetch-utils');

const VAULT_PATH = process.env.VAULT_PATH || '/Volumes/My Shared Files/StefanEternal';
const XEETS_DIR = path.join(VAULT_PATH, '00 - Inbox/Xeets to Review');
const SCRIPT_DIR = __dirname;
const FETCHED_PATH = path.join(SCRIPT_DIR, 'fetched-tweets.json');

/**
 * Parse frontmatter from markdown file
 */
function parseFrontmatter(content) {
  const match = content.match(/^---\n([\s\S]*?)\n---/);
  if (!match) return {};

  const lines = match[1].split('\n');
  const fm = {};

  for (const line of lines) {
    const [key, ...valueParts] = line.split(':');
    if (key && valueParts.length > 0) {
      fm[key.trim()] = valueParts.join(':').trim();
    }
  }

  return fm;
}

/**
 * Extract content section from markdown
 */
function extractContent(markdown) {
  const match = markdown.match(/## Content\n\n([\s\S]*?)(?:\n## |$)/);
  if (!match) return '';
  return match[1].trim();
}

/**
 * Extract author handle and name from URL and content
 */
function extractAuthor(sourceUrl, markdown) {
  // Extract handle from URL: x.com/@handle/status/id
  const handleMatch = sourceUrl.match(/x\.com\/(@?\w+)\/status/);
  const handle = handleMatch ? handleMatch[1].replace('@', '') : 'unknown';

  // Extract author name from heading (first line after frontmatter)
  const contentMatch = markdown.match(/---\n[\s\S]*?---\n\n# (.*?)\n/);
  const name = contentMatch ? contentMatch[1].trim() : handle;

  return { handle, name };
}

/**
 * Main ingestion
 */
async function main() {
  console.log('📥 Ingesting Xeets to Review...\n');

  // Check if Xeets directory exists
  if (!fs.existsSync(XEETS_DIR)) {
    console.error(`❌ Xeets directory not found: ${XEETS_DIR}`);
    process.exit(1);
  }

  // Load existing fetched tweets
  let fetched = safeReadJSON(FETCHED_PATH, []);
  const fetchedUrls = new Set(fetched.map(t => t.url.split('?')[0]));

  console.log(`Found ${fetched.length} existing fetched tweets\n`);

  // Get all Xeets files
  const xeetsFiles = fs.readdirSync(XEETS_DIR)
    .filter(f => f.endsWith('.md'))
    .sort();

  console.log(`Found ${xeetsFiles.length} Xeets files to process\n`);

  let added = 0;
  let skipped = 0;

  for (const file of xeetsFiles) {
    const filePath = path.join(XEETS_DIR, file);

    try {
      const content = fs.readFileSync(filePath, 'utf-8');
      const fm = parseFrontmatter(content);
      const sourceUrl = fm.source_url;

      if (!sourceUrl) {
        console.log(`⚠️  Skipping (no source_url): ${file}`);
        skipped++;
        continue;
      }

      const baseUrl = sourceUrl.split('?')[0];

      // Check for duplicate
      if (fetchedUrls.has(baseUrl)) {
        console.log(`⏩ Duplicate: ${baseUrl}`);
        skipped++;
        continue;
      }

      // Extract data
      const tweetContent = extractContent(content);
      const { handle, name } = extractAuthor(sourceUrl, content);

      if (!tweetContent || tweetContent.length < 1) {
        console.log(`⚠️  Skipping (no content): ${file}`);
        skipped++;
        continue;
      }

      // Create entry
      const entry = {
        url: baseUrl,
        accessible: true,
        content: tweetContent,
        author: name,
        handle: handle,
        timestamp: new Date().toISOString(),
        foundIn: ['xeets-to-review'],
        firstSeen: 'xeets-to-review'
      };

      fetched.push(entry);
      fetchedUrls.add(baseUrl);

      console.log(`✓ Added: ${baseUrl}`);
      added++;

    } catch (error) {
      console.error(`✗ Error processing ${file}: ${error.message}`);
      skipped++;
    }
  }

  // Save results
  if (added > 0) {
    fs.writeFileSync(FETCHED_PATH, JSON.stringify(fetched, null, 2));
  }

  console.log('\n================================');
  console.log(`✓ Added: ${added}`);
  console.log(`⏩ Skipped: ${skipped}`);
  console.log(`Total: ${fetched.length}`);
  console.log('================================\n');

  if (added > 0) {
    console.log(`📝 Ready to process with: node process-tweets.js`);
  }
}

main().catch(console.error);
