#!/usr/bin/env node

/**
 * Simple X.com Tweet Fetcher
 * Fetches tweet content using authenticated Playwright sessions
 * Returns raw content to Claude Code for processing
 */

const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const VAULT_PATH = process.env.VAULT_PATH || path.join(process.env.HOME, 'Library/Mobile Documents/iCloud~md~obsidian/Documents/StefanEternal');

/**
 * Scan vault for X.com and twitter.com links
 */
function scanVaultForLinks() {
  const links = new Map();

  function scanDirectory(dirPath, relativePath = '') {
    const entries = fs.readdirSync(dirPath, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(dirPath, entry.name);
      const relPath = path.join(relativePath, entry.name);

      if (entry.isDirectory()) {
        if (entry.name === 'Templates' || entry.name === 'Attachments' || entry.name === '.obsidian') {
          continue;
        }
        scanDirectory(fullPath, relPath);
      } else if (entry.name.endsWith('.md')) {
        try {
          const content = fs.readFileSync(fullPath, 'utf-8');
          const urlRegex = /https?:\/\/(x\.com|twitter\.com)\/[^\s\)]+/g;
          const matches = content.matchAll(urlRegex);

          for (const match of matches) {
            let url = match[0];
            const baseUrl = url.split('?')[0];

            // Only include actual tweets (has /status/ or /article/)
            if (!baseUrl.includes('/status/') && !baseUrl.includes('/article/')) {
              continue;
            }

            if (!links.has(baseUrl)) {
              links.set(baseUrl, {
                url: url,
                baseUrl: baseUrl,
                files: [relPath],
                firstSeen: relPath
              });
            } else {
              const existing = links.get(baseUrl);
              if (!existing.files.includes(relPath)) {
                existing.files.push(relPath);
              }
            }
          }
        } catch (err) {
          // Skip unreadable files
        }
      }
    }
  }

  scanDirectory(VAULT_PATH);
  return Array.from(links.values());
}

/**
 * Fetch tweet content using Playwright
 */
async function fetchTweetContent(context, url) {
  const page = await context.newPage();

  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 15000 });

    // Wait for tweet content to load (article element contains tweets)
    try {
      await page.waitForSelector('article', { timeout: 8000 });
      await page.waitForTimeout(2000); // Extra wait for content to render
    } catch (e) {
      // If no article found, might be login wall or error
    }

    // Check for login wall
    const hasLoginWall = await page.locator('text=Sign in to X').count() > 0 ||
                         await page.locator('text=Log in to X').count() > 0 ||
                         await page.locator('text=Don\'t miss what\'s happening').count() > 0;

    if (hasLoginWall) {
      return {
        url: url,
        accessible: false,
        error: 'Login wall detected',
        timestamp: new Date().toISOString()
      };
    }

    // Extract tweet content from article elements
    const textContent = await page.evaluate(() => {
      const articles = document.querySelectorAll('article');
      let content = '';
      articles.forEach((article, i) => {
        const text = article.innerText || article.textContent;
        if (i === 0) {
          content = text; // Main tweet is first article
        }
      });
      return content || document.body.innerText;
    });

    return {
      url: url,
      accessible: true,
      content: textContent,
      timestamp: new Date().toISOString()
    };
  } catch (error) {
    return {
      url: url,
      accessible: false,
      error: error.message,
      timestamp: new Date().toISOString()
    };
  } finally {
    await page.close();
  }
}

/**
 * Main function
 */
async function main() {
  console.log('🔗 X.com Tweet Fetcher\n');

  // Scan for links
  console.log('Scanning vault for X.com/Twitter links...');
  const links = scanVaultForLinks();
  console.log(`Found ${links.length} tweet link(s)\n`);

  if (links.length === 0) {
    console.log('No links found in vault.');
    return;
  }

  // Load cookies
  const cookiesPath = path.join(__dirname, '.cookies.json');
  let cookies = null;
  if (fs.existsSync(cookiesPath)) {
    console.log('Loading authentication cookies...');
    cookies = JSON.parse(fs.readFileSync(cookiesPath, 'utf-8'));
  } else {
    console.log('⚠️  No .cookies.json found. Running without authentication.');
    console.log('   See COOKIE_SETUP.md for instructions.\n');
  }

  // Launch browser
  console.log('Launching browser...\n');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });

  if (cookies) {
    await context.addCookies(cookies);
    console.log('✓ Authenticated session loaded\n');
  }

  // Fetch tweets
  const results = [];
  let fetched = 0;
  let failed = 0;

  for (const link of links) {
    console.log(`Fetching: ${link.baseUrl}`);

    const result = await fetchTweetContent(context, link.url);
    result.foundIn = link.files;
    result.firstSeen = link.firstSeen;

    if (result.accessible) {
      console.log('  ✓ Success');
      fetched++;
    } else {
      console.log(`  ✗ Failed: ${result.error || 'Login wall'}`);
      failed++;
    }

    results.push(result);

    // Rate limiting
    await new Promise(resolve => setTimeout(resolve, 2000));
  }

  // Close browser
  await context.close();
  await browser.close();

  // Save results
  const outputPath = path.join(__dirname, 'fetched-tweets.json');
  fs.writeFileSync(outputPath, JSON.stringify(results, null, 2));

  console.log('\n================================');
  console.log(`✓ Fetched: ${fetched}`);
  console.log(`✗ Failed: ${failed}`);
  console.log(`Success Rate: ${((fetched / links.length) * 100).toFixed(1)}%`);
  console.log('================================\n');
  console.log(`Results saved to: fetched-tweets.json`);
}

main().catch(console.error);
