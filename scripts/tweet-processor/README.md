# Xeet Screenshot Processor

Automatically process X (Twitter) post screenshots from iOS and create organized, categorized notes in your Obsidian vault using AI vision.

## Features

- Extracts text, author, dates, and engagement metrics from X post screenshots
- Uses AI (Gemini Flash or Claude Vision) to categorize and summarize xeets
- **Confidence-based routing** - uncertain categorizations go to Inbox for manual review
- Auto-generates formatted markdown notes in your PARA-organized Obsidian vault
- Supports both manual execution and automated cron scheduling
- Easy to switch between AI providers (currently: Gemini, future: Claude)

## How It Works

```
1. Screenshot xeet on iOS
2. Share to Obsidian → Attachments/Xeets/
3. Run processor (manual or cron)
4. AI analyzes screenshot and assigns confidence score
5. Routes to appropriate folder:
   - High confidence (≥0.7) → Resources or Projects
   - Low confidence (<0.7) → Inbox for manual review
6. Creates organized note with AI insights
7. Logs to processing history
```

## Prerequisites

- Node.js (v18+)
- Obsidian vault organized with PARA method
- Google AI API key (free tier available at https://makersuite.google.com/app/apikey)

## Installation

### 1. Install Dependencies

```bash
cd tweet-processor
npm install
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your Google AI API key
nano .env
```

**Required settings in `.env`:**
```bash
GOOGLE_API_KEY=your_google_ai_api_key_here
VAULT_PATH=/Users/gw/Library/Mobile Documents/iCloud~md~obsidian/Documents/StefanEternal
AI_PROVIDER=gemini
```

### 3. Get Your Google AI API Key

1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key and paste it into `.env`

## Usage

### Manual Execution

Run the processor manually:

```bash
# Process all new screenshots
npm run process

# Dry run (preview without making changes)
npm run test
```

### As a Claude Code Skill

Add this as a slash command in Claude Code:

**Option A: Using the skill script**
```bash
# In Claude Code, run:
# (This assumes you have skills set up in your Claude Code config)
/process-tweets
```

**Option B: Direct execution from Claude Code**
Just ask Claude Code:
```
"Run the tweet processor in ~/Workspace/mindmap/tweet-processor"
```

### Automated with Cron

Run automatically every night at 2 AM:

```bash
# Edit crontab
crontab -e

# Add this line:
0 2 * * * cd /Users/gw/Workspace/mindmap/tweet-processor && /usr/local/bin/node process-tweets.js >> ~/logs/tweet-processor.log 2>&1
```

**Using PM2 (recommended for better process management):**

```bash
# Install PM2
npm install -g pm2

# Run with cron schedule
pm2 start process-tweets.js --cron "0 2 * * *" --name tweet-processor

# Save PM2 configuration
pm2 save
pm2 startup
```

## How to Use

### 1. Capture Tweets on iOS

When you see a tweet you want to save:
1. Take a screenshot (side button + volume up)
2. Tap the screenshot thumbnail
3. Share → Obsidian → Save to `Attachments/Xeets/`

### 2. Process Screenshots

Run manually or wait for cron:
```bash
npm run process
```

### 3. Review Generated Notes

The processor will create notes in:
- **Resources:** `03 - Resources/X Insights/` (for learning/reference tweets)
- **Project Ideas:** `01 - Projects/Ideas/` (for tweets that inspire projects)

Each note includes:
- Extracted tweet text
- Author information
- Engagement metrics (likes, retweets, replies)
- AI-generated summary and insights
- Suggested tags
- Link to original screenshot

### 4. Check Processing Log

View processing history:
```
00 - Inbox/Tweet Processing Log.md
```

## Output Example

**Generated note:** `03 - Resources/X Insights/building-rag-systems-with-claude.md`

```markdown
---
created: 2026-01-05
source: twitter
author: @swyx
author_name: Shawn Wang
tags: ["ai", "rag", "claude", "llm"]
category: resource
confidence: 0.92
screenshot: "[[Attachments/Xeets/IMG_1234.png]]"
---

# Building RAG Systems with Claude

**Author:** Shawn Wang (@swyx)
**Date:** 2026-01-04
**Engagement:** 1.2K ❤️ · 234 🔄 · 89 💬

## Tweet Content

> Just shipped a RAG system using Claude's 200K context window.
> Game changer for technical documentation search.
> No more chunking headaches! 🚀

![[Attachments/Xeets/IMG_1234.png]]

## Key Insights

Claude's extended context window enables RAG implementations without complex chunking strategies, simplifying architecture for documentation search systems.

## Relevance

Directly applicable to current Alchemer Ash project which uses RAG for Slack bot. Could eliminate chunking complexity and improve response quality by leveraging full context windows.

## Related Notes

-

---
**Captured from:** [[00 - Inbox/📥 Quick Capture|Quick Capture]]
**Screenshot:** [[Attachments/Xeets/IMG_1234.png]]
```

## Configuration

### Vault Structure

The processor expects this PARA structure:
```
StefanEternal/
├── 00 - Inbox/
│   ├── Xeets to Review/ (low-confidence xeets for manual review)
│   └── Xeet Processing Log.md (auto-generated)
├── 01 - Projects/
│   └── Ideas/ (high-confidence project-idea xeets)
├── 03 - Resources/
│   └── X Insights/ (high-confidence resource xeets)
└── Attachments/
    └── Xeets/ (put screenshots here)
```

### Confidence-Based Routing

The processor uses AI confidence scoring to ensure quality categorization:

**How it works:**
1. AI analyzes the screenshot and assigns a confidence score (0.0 - 1.0)
2. High confidence (≥0.7) → Automatically filed in Resources or Projects
3. Low confidence (<0.7) → Routed to `00 - Inbox/Xeets to Review/` for manual review

**Why this matters:**
- Prevents miscategorization of ambiguous tweets
- Catches tweets that might not be relevant to your work
- Integrates with your weekly inbox review workflow
- You make the final decision on uncertain items

**Adjusting the threshold:**
Edit `.env` to change sensitivity:
```bash
CONFIDENCE_THRESHOLD=0.7  # Default (recommended: 0.6 - 0.8)
```

- Lower (0.6) = More automatic filing, some miscategorizations
- Higher (0.8) = More manual review, fewer mistakes

**Example confidence scores:**
- 0.95 = Crystal clear (e.g., "Here's a tutorial on building RAG systems")
- 0.75 = Pretty clear (e.g., technical insight that's clearly a resource)
- 0.55 = Uncertain (e.g., could be interesting but not clearly relevant)
- 0.30 = Very unclear (e.g., random meme, off-topic content)

### AI Provider Configuration

**Current: Gemini Flash (Free Credits)**
```bash
AI_PROVIDER=gemini
GOOGLE_API_KEY=your_key
```

**Future: Claude Vision (Better Categorization)**

When you're ready to switch to Claude:

1. Get Anthropic API key from https://console.anthropic.com/
2. Update `.env`:
   ```bash
   AI_PROVIDER=claude
   ANTHROPIC_API_KEY=your_claude_key
   ```
3. Install Claude SDK:
   ```bash
   npm install @anthropic-ai/sdk
   ```
4. Update `process-tweets.js` (see section below)

## Switching from Gemini to Claude

The code is structured to make switching easy. When ready:

1. Uncomment the Claude client initialization in `process-tweets.js` (lines ~40-45)
2. Implement `analyzeScreenshotClaude()` function (similar to existing Gemini function)
3. Update `.env` to use `AI_PROVIDER=claude`

The rest of the code (screenshot finding, note generation, logging) remains unchanged.

## Troubleshooting

### No screenshots found
- Check that screenshots are in `Attachments/Xeets/` folder
- Ensure vault path is correct in `.env`

### API errors
- Verify API key is correct
- Check you have free credits remaining (https://makersuite.google.com/)
- Try with `--dry-run` to test without API calls

### Permission errors
- Ensure script has read/write access to vault directory
- Check Obsidian isn't locking files (close vault if needed)

### Cron not running
- Check cron logs: `tail -f ~/logs/tweet-processor.log`
- Verify node path: `which node`
- Test manual execution first

## Cost Estimates

### Gemini Flash (Current)
- **Free tier:** 1,500 requests/day
- **Paid:** ~$0.000125 per image
- **Monthly cost (60 tweets):** ~$0.0075 (essentially free)

### Claude Vision (Future)
- **Cost:** ~$0.003 per image
- **Monthly cost (60 tweets):** ~$0.18

## Development

### Project Structure
```
tweet-processor/
├── process-tweets.js          # Main script
├── package.json               # Dependencies
├── .env                       # Configuration (not in git)
├── .env.example               # Example configuration
├── .processed-tweets.json     # Tracking file (auto-generated)
├── process-tweets.skill.sh    # Claude Code skill wrapper
└── README.md                  # This file
```

### Testing

```bash
# Dry run - preview without changes
npm run test

# Process a single screenshot manually
node process-tweets.js
```

### Logs

Check processing results:
- **Obsidian:** `00 - Inbox/Tweet Processing Log.md`
- **Cron logs:** `~/logs/tweet-processor.log`
- **Processed tracking:** `.processed-tweets.json`

## Future Enhancements

- [ ] Thread detection (multi-tweet threads)
- [ ] Video thumbnail extraction
- [ ] Bulk reprocessing of old screenshots
- [ ] Custom categorization rules
- [ ] Integration with Daily Notes
- [ ] Auto-tagging based on content analysis
- [ ] Duplicate detection

## Related Projects

This tool complements your Alchemer sprint:
- **Ash Slackbot:** Similar AI-powered content processing
- **Claude API Survey Builder:** Reusable Claude API patterns
- **Chrome Extension:** Could capture tweets directly from browser

## License

MIT

## Support

For issues or questions:
1. Check `Tweet Processing Log.md` in your vault
2. Run with `--dry-run` to debug
3. Review logs in `~/logs/tweet-processor.log`

---

**Built for the PARA method** | **Powered by Gemini Flash** | **Ready for Claude Vision**
