#!/usr/bin/env node

/**
 * Fetch Bookmarked Tweets from X.com
 * Requires authenticated cookies in .cookies.json
 */

const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const { safeReadJSON } = require('./lib/fetch-utils');

const VAULT_PATH = process.env.VAULT_PATH || path.join(process.env.HOME, 'Library/Mobile Documents/iCloud~md~obsidian/Documents/StefanEternal');

/**
 * Fetch bookmarked tweet URLs
 */
async function fetchBookmarkUrls(context, maxScrolls = 5) {
  const page = await context.newPage();
  const urls = new Set();

  try {
    console.log('📚 Navigating to bookmarks page...');
    await page.goto('https://x.com/i/bookmarks', { waitUntil: 'domcontentloaded', timeout: 15000 });
    await page.waitForTimeout(3000);

    // Check authentication
    const hasLoginWall = await page.locator('text=Sign in to X').count() > 0 ||
                         await page.locator('text=Log in to X').count() > 0;

    if (hasLoginWall) {
      throw new Error('Login required - cookies may be invalid');
    }

    console.log('✓ Authenticated, loading bookmarks...\n');

    // Scroll and collect URLs
    for (let i = 0; i < maxScrolls; i++) {
      console.log(`Scroll ${i + 1}/${maxScrolls}...`);

      // Extract tweet links from current view
      const newUrls = await page.evaluate(() => {
        const links = Array.from(document.querySelectorAll('a[href*="/status/"]'));
        return links
          .map(a => a.href)
          .filter(href => href.includes('/status/'))
          .map(href => href.split('?')[0]); // Remove query params
      });

      const before = urls.size;
      newUrls.forEach(url => urls.add(url));
      const added = urls.size - before;

      console.log(`  Found ${newUrls.length} links, ${added} new (total: ${urls.size})`);

      // Scroll to load more
      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
      await page.waitForTimeout(2000);

      // If no new URLs found, we've reached the end
      if (added === 0 && i > 1) {
        console.log('  No new bookmarks found, stopping scroll');
        break;
      }
    }

    console.log(`\n✓ Collected ${urls.size} unique bookmark URLs`);
    return Array.from(urls);

  } catch (error) {
    console.error('Error fetching bookmarks:', error.message);
    return [];
  } finally {
    await page.close();
  }
}

/**
 * Main function
 */
async function main() {
  console.log('🔖 X.com Bookmark Fetcher\n');

  // Load cookies
  const cookiesPath = path.join(__dirname, '.cookies.json');
  if (!fs.existsSync(cookiesPath)) {
    console.error('❌ No .cookies.json found');
    console.error('   Run: See COOKIE_SETUP.md for instructions\n');
    process.exit(1);
  }

  const cookies = safeReadJSON(cookiesPath, null);
  if (!cookies) {
    console.error('❌ Failed to parse .cookies.json');
    process.exit(1);
  }
  console.log('✓ Loaded authentication cookies\n');

  // Launch browser
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });

  await context.addCookies(cookies);

  // Fetch bookmark URLs
  const maxScrolls = parseInt(process.env.MAX_SCROLLS) || 10;
  const bookmarkUrls = await fetchBookmarkUrls(context, maxScrolls);

  await browser.close();

  if (bookmarkUrls.length === 0) {
    console.log('\n⚠️  No bookmarks found');
    return;
  }

  // Save URLs to file
  const outputPath = path.join(__dirname, 'bookmarked-urls.json');
  const bookmarks = bookmarkUrls.map(url => ({
    url: url,
    baseUrl: url.split('?')[0],
    fetchedAt: new Date().toISOString()
  }));

  fs.writeFileSync(outputPath, JSON.stringify(bookmarks, null, 2));

  console.log('\n================================');
  console.log(`✓ Saved ${bookmarks.length} bookmark URLs`);
  console.log(`📁 Output: bookmarked-urls.json`);
  console.log('================================\n');
  console.log('Next step: Run npm run fetch to download tweet content');
}

main().catch(console.error);
