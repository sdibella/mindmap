/**
 * Shared utilities for tweet-processor scripts
 */

const fs = require('fs');

/**
 * Safely read and parse a JSON file.
 * Returns fallback value if file doesn't exist or is corrupt.
 */
function safeReadJSON(filePath, fallback = null) {
  if (!fs.existsSync(filePath)) return fallback;
  try {
    return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
  } catch (err) {
    console.error(`Warning: Failed to parse ${filePath}: ${err.message}`);
    return fallback;
  }
}

/**
 * Fetch tweet content using a Playwright browser context.
 * Shared between fetch-tweets.js and fetch-batch.js.
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

module.exports = { safeReadJSON, fetchTweetContent };
