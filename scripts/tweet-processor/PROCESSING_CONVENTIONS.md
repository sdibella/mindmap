# Tweet Processing Conventions

## Folder Routing Rules

### High Confidence (≥0.85)
Auto-file to appropriate folder based on category and topic matching.

### Medium Confidence (0.70-0.84)
Route to Inbox subfolder for manual review with suggested folder in frontmatter.

### Low Confidence (<0.70)
Route to Inbox subfolder for manual review.

## Inbox Organization

**IMPORTANT:** All low-confidence tweets MUST go to:
```
00 - Inbox/Xeets to Review/
```

**NOT** directly in `00 - Inbox/`

This keeps the Inbox organized if processing falls behind.

## Folder Creation

Create new folders automatically when:
- Content confidence ≥0.85
- Topic doesn't match existing folders
- Clear category assignment

Example new folders created:
- `03 - Resources/Sales` (created during pilot)
- `03 - Resources/Marketing` (future)
- `02 - Areas/Productivity` (future)

## Project Linking

Automatically link notes to projects when tweet content mentions:
- "Boomer AI" → [[Boomer AI]]
- "Alchemer" → [[Alchemer]]
- "PolyMarket" → [[PolyMarket TradeBots]]
- "GoFigurine" → [[GoFigurineMe]]

## Note Naming

Use descriptive kebab-case filenames:
- `claude-code-hyperstructures-ai-coding.md` ✓
- `tweet-123.md` ✗

## Frontmatter Requirements

```yaml
---
created: YYYY-MM-DD
source: x.com
source_url: https://x.com/...
author: "@username"
tags: ["tag1", "tag2"]
category: resource|area|review-needed
topic: Topic Name
confidence: 0.XX
folder_confidence: 0.XX
auto_filed: true|false
folder_created: true|false  # if new folder was created
---
```

## Processing Workflow

1. Fetch tweets with `npm run fetch`
2. Scan folders with `npm run scan-folders`
3. Process with Claude Code:
   - Analyze content
   - Determine category and topic
   - Match to existing folders
   - Route based on confidence
   - Create formatted note
   - Link to related projects
4. Mark processed with `npm run mark-processed <url>`
5. Review Inbox items periodically

## Deduplication

Tweets are tracked in `.processed-links.json` by base URL (query params stripped).

Check unprocessed with: `npm run check-processed`
