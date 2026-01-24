# Authenticated X.com Scraping Pilot Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build authenticated X.com content fetcher that scrapes vault links and returns raw content to Claude Code for intelligent processing and vault organization.

**Architecture:** Simple Node.js fetcher script using Playwright with cookie auth to extract tweet content. All AI analysis, categorization, and folder routing happens in Claude Code using the user's existing Max subscription. No API costs.

**Tech Stack:** Node.js, Playwright (authenticated sessions), filesystem scanning. AI processing handled by Claude Code.

---

## Task 1: Cookie Authentication Setup

**Files:**
- Create: `scripts/tweet-processor/.cookies.json.example`
- Modify: `scripts/tweet-processor/.gitignore`
- Create: `scripts/tweet-processor/COOKIE_SETUP.md`

**Step 1: Create cookie example file**

Create `scripts/tweet-processor/.cookies.json.example`:

```json
[
  {
    "name": "auth_token",
    "value": "your_auth_token_here",
    "domain": ".x.com",
    "path": "/",
    "httpOnly": true,
    "secure": true,
    "sameSite": "None"
  },
  {
    "name": "ct0",
    "value": "your_csrf_token_here",
    "domain": ".x.com",
    "path": "/",
    "httpOnly": false,
    "secure": true,
    "sameSite": "Lax"
  }
]
```

**Step 2: Update .gitignore**

Add to `scripts/tweet-processor/.gitignore`:

```
.cookies.json
pilot-results.json
fetched-tweets.json
```

**Step 3: Create cookie setup instructions**

Create `scripts/tweet-processor/COOKIE_SETUP.md`:

```markdown
# Cookie Authentication Setup

## Option 1: Browser DevTools (Recommended)

1. Open X.com in your browser and log in
2. Open DevTools (F12 or Cmd+Option+I)
3. Go to Application > Storage > Cookies > https://x.com
4. Find these cookies and copy their values:
   - `auth_token`
   - `ct0`
5. Create `.cookies.json` in this directory using `.cookies.json.example` as template
6. Paste the cookie values

## Option 2: Browser Extension

1. Install "EditThisCookie" or "Cookie-Editor" extension
2. Visit X.com while logged in
3. Export cookies as JSON
4. Save to `.cookies.json` in this directory

## Security Note

Never commit `.cookies.json` to git. It contains authentication credentials.
```

**Step 4: Commit**

```bash
git add scripts/tweet-processor/.cookies.json.example scripts/tweet-processor/.gitignore scripts/tweet-processor/COOKIE_SETUP.md
git commit -m "feat: add cookie authentication setup for x.com scraping"
```

---

## Task 2: Simple Tweet Fetcher Script

**Files:**
- Create: `scripts/tweet-processor/fetch-tweets.js`

**Step 1: Create fetch-tweets.js**

Create `scripts/tweet-processor/fetch-tweets.js`:

```javascript
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
    await page.waitForTimeout(3000);

    const textContent = await page.textContent('body');

    const hasLoginWall = await page.locator('text=Sign in to X').count() > 0 ||
                         await page.locator('text=Log in to X').count() > 0 ||
                         await page.locator('text=Don\'t miss what\'s happening').count() > 0;

    return {
      url: url,
      accessible: !hasLoginWall,
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
```

**Step 2: Make executable**

```bash
chmod +x scripts/tweet-processor/fetch-tweets.js
```

**Step 3: Update package.json**

Modify `scripts/tweet-processor/package.json`:

```json
{
  "name": "xeet-link-processor",
  "version": "3.0.0",
  "description": "Fetch X.com links from Obsidian vault for Claude Code processing",
  "main": "fetch-tweets.js",
  "scripts": {
    "fetch": "node fetch-tweets.js"
  },
  "keywords": ["obsidian", "twitter", "x.com", "automation", "claude"],
  "author": "",
  "license": "MIT",
  "dependencies": {
    "playwright": "^1.49.0"
  }
}
```

**Step 4: Test the fetcher**

```bash
cd scripts/tweet-processor
npm run fetch
```

Expected output:
- Vault scanned
- Links found
- Browser launched
- Tweets fetched
- Results saved to `fetched-tweets.json`

**Step 5: Commit**

```bash
git add scripts/tweet-processor/fetch-tweets.js scripts/tweet-processor/package.json
git commit -m "feat: create simple tweet content fetcher for Claude Code processing"
```

---

## Task 3: Vault Folder Scanner

**Files:**
- Create: `scripts/tweet-processor/scan-vault-folders.js`

**Step 1: Create folder scanner**

Create `scripts/tweet-processor/scan-vault-folders.js`:

```javascript
#!/usr/bin/env node

/**
 * Scan vault folder structure for Claude Code
 * Returns existing folders in Resources, Areas, and Projects
 */

const fs = require('fs');
const path = require('path');

const VAULT_PATH = process.env.VAULT_PATH || path.join(process.env.HOME, 'Library/Mobile Documents/iCloud~md~obsidian/Documents/StefanEternal');

function scanVaultFolders() {
  const folders = {
    resources: [],
    areas: [],
    projects: []
  };

  function scanDir(basePath, type) {
    const fullPath = path.join(VAULT_PATH, basePath);
    if (!fs.existsSync(fullPath)) return;

    const entries = fs.readdirSync(fullPath, { withFileTypes: true });
    for (const entry of entries) {
      if (entry.isDirectory() && !entry.name.startsWith('.')) {
        folders[type].push({
          name: entry.name,
          relativePath: path.join(basePath, entry.name),
          fullPath: path.join(fullPath, entry.name)
        });
      }
    }
  }

  scanDir('03 - Resources', 'resources');
  scanDir('02 - Areas', 'areas');
  scanDir('01 - Projects', 'projects');

  return folders;
}

// Run and output JSON
const folders = scanVaultFolders();
console.log(JSON.stringify(folders, null, 2));
```

**Step 2: Make executable**

```bash
chmod +x scripts/tweet-processor/scan-vault-folders.js
```

**Step 3: Add to package.json**

Modify `scripts/tweet-processor/package.json` scripts:

```json
{
  "scripts": {
    "fetch": "node fetch-tweets.js",
    "scan-folders": "node scan-vault-folders.js"
  }
}
```

**Step 4: Test folder scanner**

```bash
npm run scan-folders
```

Expected: JSON output of existing folders

**Step 5: Commit**

```bash
git add scripts/tweet-processor/scan-vault-folders.js scripts/tweet-processor/package.json
git commit -m "feat: add vault folder structure scanner"
```

---

## Task 4: Processed Links Tracker

**Files:**
- Create: `scripts/tweet-processor/check-processed.js`
- Create: `scripts/tweet-processor/mark-processed.js`

**Step 1: Create check-processed script**

Create `scripts/tweet-processor/check-processed.js`:

```javascript
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
```

**Step 2: Create mark-processed script**

Create `scripts/tweet-processor/mark-processed.js`:

```javascript
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
```

**Step 3: Make scripts executable**

```bash
chmod +x scripts/tweet-processor/check-processed.js
chmod +x scripts/tweet-processor/mark-processed.js
```

**Step 4: Add to package.json**

```json
{
  "scripts": {
    "fetch": "node fetch-tweets.js",
    "scan-folders": "node scan-vault-folders.js",
    "check-processed": "node check-processed.js",
    "mark-processed": "node mark-processed.js"
  }
}
```

**Step 5: Test tracking**

```bash
npm run check-processed
```

Expected: JSON array of unprocessed tweets

**Step 6: Commit**

```bash
git add scripts/tweet-processor/check-processed.js scripts/tweet-processor/mark-processed.js scripts/tweet-processor/package.json
git commit -m "feat: add processed links tracking utilities"
```

---

## Task 5: Update Documentation

**Files:**
- Create: `scripts/tweet-processor/README.md`
- Modify: `scripts/tweet-processor/.env.example`

**Step 1: Create README**

Create `scripts/tweet-processor/README.md`:

```markdown
# X.com Authenticated Tweet Fetcher

Simple authenticated scraper that fetches tweet content from links in your Obsidian vault. Designed to work with Claude Code for AI-powered processing and organization.

## Architecture

**Tweet Fetcher (Node.js):**
- Scans vault for X.com/Twitter links
- Uses Playwright with cookies for authentication
- Fetches raw tweet content
- Returns JSON for Claude Code processing

**Claude Code (AI Processing):**
- Analyzes tweet content
- Categorizes and routes to folders
- Generates formatted notes
- Handles all intelligent decisions

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Set Up Authentication

Follow `COOKIE_SETUP.md` to export your X.com cookies to `.cookies.json`.

### 3. Fetch Tweets

```bash
npm run fetch
```

This creates `fetched-tweets.json` with all tweet content.

### 4. Process with Claude Code

Open Claude Code in this directory and ask:

> "Process the fetched tweets and organize them into my vault"

Claude Code will:
- Analyze each tweet
- Determine category and topic
- Match to existing folders or create new ones
- Generate formatted markdown notes
- Link to related projects
- Save to appropriate PARA locations

## Available Scripts

- `npm run fetch` - Scan vault and fetch tweet content
- `npm run scan-folders` - List existing vault folders
- `npm run check-processed` - Show unprocessed tweets
- `npm run mark-processed <url>` - Mark a URL as processed

## Files

- `fetched-tweets.json` - Raw tweet content (generated)
- `.processed-links.json` - Tracking file (generated)
- `.cookies.json` - Your auth cookies (not in git)

## Workflow

1. Run `npm run fetch` to get tweet content
2. Ask Claude Code to process and organize
3. Review the created notes
4. Repeat as needed

## Security

Never commit `.cookies.json` - it contains authentication credentials.
```

**Step 2: Simplify .env.example**

Modify `scripts/tweet-processor/.env.example`:

```bash
# Optional: Override default vault path
# VAULT_PATH=/path/to/your/obsidian/vault
```

**Step 3: Commit**

```bash
git add scripts/tweet-processor/README.md scripts/tweet-processor/.env.example
git commit -m "docs: add README for Claude Code workflow"
```

---

## Task 6: Clean Up Old Files

**Files:**
- Delete: `scripts/tweet-processor/process-xeet-links.js`
- Delete: `scripts/tweet-processor/process-links-simple.js`
- Modify: `scripts/tweet-processor/package.json`

**Step 1: Remove old scripts**

```bash
git rm scripts/tweet-processor/process-xeet-links.js
git rm scripts/tweet-processor/process-links-simple.js
```

**Step 2: Remove Anthropic SDK dependency**

Modify `scripts/tweet-processor/package.json`:

```json
{
  "name": "xeet-link-processor",
  "version": "3.0.0",
  "description": "Fetch X.com links from Obsidian vault for Claude Code processing",
  "main": "fetch-tweets.js",
  "scripts": {
    "fetch": "node fetch-tweets.js",
    "scan-folders": "node scan-vault-folders.js",
    "check-processed": "node check-processed.js",
    "mark-processed": "node mark-processed.js"
  },
  "keywords": ["obsidian", "twitter", "x.com", "automation", "claude"],
  "author": "",
  "license": "MIT",
  "dependencies": {
    "playwright": "^1.49.0"
  }
}
```

**Step 3: Remove unused packages**

```bash
npm uninstall @anthropic-ai/sdk dotenv
```

**Step 4: Commit cleanup**

```bash
git add scripts/tweet-processor/package.json scripts/tweet-processor/package-lock.json
git commit -m "refactor: remove old scripts and API dependencies for Claude Code workflow"
```

---

## Success Criteria

- [ ] Cookie authentication setup documented
- [ ] Fetcher script scans vault and finds links
- [ ] Fetcher loads cookies and creates authenticated session
- [ ] Fetcher successfully fetches tweet content
- [ ] Results saved to `fetched-tweets.json`
- [ ] Folder scanner returns vault structure
- [ ] Processed link tracking works
- [ ] No API dependencies (Anthropic SDK removed)
- [ ] README documents Claude Code workflow
- [ ] No sensitive files in git

## Next Steps: Claude Code Processing

After running `npm run fetch`, use Claude Code to:

1. Read `fetched-tweets.json`
2. Read `scan-vault-folders.js` output
3. For each tweet:
   - Analyze content and categorize
   - Match to existing folder or create new
   - Generate formatted markdown note
   - Link to related projects
   - Save to appropriate location
4. Mark processed with `mark-processed.js`
5. Generate pilot summary report
