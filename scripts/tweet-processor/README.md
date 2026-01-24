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
