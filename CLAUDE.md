# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository is a tooling and automation layer for the **StefanEternal Obsidian vault** — an AI-focused knowledge base built from bookmarked tweets. The vault is NOT a personal notes system; it's a structured collection of processed X (Twitter) bookmarks organized into atomic notes with intelligent backlinking.

The actual vault lives in `StefanEternal/` (gitignored). This repo contains the scripts and docs that power the **OPENCLAW Vault Intelligence System**.

## Repository Structure

```
mindmap/
├── StefanEternal/              # Obsidian vault (gitignored)
├── scripts/tweet-processor/    # OPENCLAW automation scripts
│   ├── prompts/                      # OpenClaw agent prompts (v2)
│   │   ├── nightly-categorize.md     # Nightly: AI-powered categorization
│   │   ├── weekly-review.md          # Weekly: quality audit + fixes
│   │   └── monthly-synthesis.md      # Monthly: deep analysis + evolution
│   ├── processing-state.json         # Incremental processing cursor
│   ├── review-queue.json             # Unprocessed items from ingest
│   ├── fetch-bookmarks.js            # Ingest: fetch X bookmarks
│   ├── ingest-xeets.js              # Ingest: process into review queue
│   ├── validate-bidirectional.py     # Audit: check link integrity
│   ├── validate-graph.py            # Audit: check graph health
│   └── _retired/                     # Archived v1 Python scripts
└── docs/Vault Intelligence System/   # OPENCLAW documentation
    └── OPENCLAW_VAULT_INTELLIGENCE_PROTOCOL.md  # Master rules (read this first)
```

## Vault Structure

```
StefanEternal/
├── atoms/          # Individual tweet-based knowledge atoms (the core content)
├── maps/           # Maps of Content (MOCs) linking related atoms by topic
├── Memory/         # ClawVault memory files (OPENCLAW's persistent state)
├── 00 - Inbox/     # Staging area for unprocessed tweets
├── _archive/       # Archived/inactive atoms
├── _templates/     # Note templates
├── Daily Notes/    # Date-based notes
├── reports/        # Generated reports
└── logs/           # System logs
```

## The Atom System

The vault uses an **AI-native atom model**, not PARA. Each atom is a self-contained knowledge unit:

- One tweet → one atom in `atoms/`
- YAML frontmatter: `tags`, `created`, `updated`, `source`, `author`, `type: tweet`, `confidence`, `entities`
- Backlinks connect related atoms via `[[atom-name]]` syntax
- MOC files in `maps/` aggregate atoms by topic (ai-agents, crypto-defi, prediction-markets, etc.)

## OPENCLAW System (v2 — AI-Powered)

The **Vault Intelligence System** uses OpenClaw agent prompts (not Python regex) for categorization and backlinking. The AI reads content, understands it, and creates properly categorized atoms with wiki-links in one pass.

**Architecture:**
```
review-queue.json → OpenClaw agent (prompt) → atom files with wiki-links
                    ↑ reads protocol doc        ↑ writes directly
                    ↑ reads existing atoms       ↑ marks items processed
                    ↑ AutoRouter picks model     ↑ updates state cursor
```

**Cron jobs** (on VM `finn@finns-virtual-machine`):
| Schedule | Prompt | Purpose |
|----------|--------|---------|
| Daily 1 AM | `npm run pipeline` | Fetch new bookmarks → review queue |
| Daily 2 AM | `prompts/nightly-categorize.md` | Process ≤20 new items into atoms |
| Monday 8 AM | `prompts/weekly-review.md` | Audit quality, fix issues |
| 1st of month | `prompts/monthly-synthesis.md` | Deep analysis, propose protocol changes |

- **10 primary categories:** ai-agents, prediction-markets, crypto-defi, software-development, ai-models-research, stock-trading-finance, business-entrepreneurship, systems-architecture, learning-resources, people-personas
- **Protocol doc:** `docs/Vault Intelligence System/OPENCLAW_VAULT_INTELLIGENCE_PROTOCOL.md` — single source of truth for all categorization rules
- **ClawVault Memory:** `StefanEternal/Memory/` — OPENCLAW's persistent memory and indexes (e.g., `X Bookmarks.md`)

## Working with the Vault

- Files in `StefanEternal/` must NOT be committed to git
- Default to read-safe operations — confirm before bulk modifications
- Preserve existing atom structure and YAML frontmatter
- Obsidian links use `[[Note Name]]` or `[[Note Name|Display Text]]` format
- When in doubt, check the protocol doc before categorizing or linking

## Workflow Orchestration

### 1. Plan Mode Default
- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
- If something goes sideways, STOP and re-plan immediately – don't keep pushing
- Write detailed specs upfront to reduce ambiguity

### 2. Subagent Strategy
- Use subagents liberally to keep main context window clean
- Offload research, exploration, and parallel analysis to subagents
- One task per subagent for focused execution

### 3. Self-Improvement Loop
- After ANY correction from the user: update `tasks/lessons.md` with the pattern
- Write rules for yourself that prevent the same mistake
- Review lessons at session start for relevant project

### 4. Verification Before Done
- Never mark a task complete without proving it works
- Run tests, check logs, demonstrate correctness
- Ask yourself: "Would a staff engineer approve this?"

### 5. Demand Elegance (Balanced)
- For non-trivial changes: pause and ask "is there a more elegant way?"
- Skip this for simple, obvious fixes – don't over-engineer

### 6. Autonomous Bug Fixing
- When given a bug report: just fix it. Don't ask for hand-holding
- Point at logs, errors, failing tests – then resolve them

## Task Management

1. **Plan First**: Write plan to `tasks/todo.md` with checkable items
2. **Verify Plan**: Check in before starting implementation
3. **Track Progress**: Mark items complete as you go
4. **Explain Changes**: High-level summary at each step
5. **Capture Lessons**: Update `tasks/lessons.md` after corrections

## Core Principles

- **Simplicity First**: Make every change as simple as possible. Impact minimal code.
- **No Laziness**: Find root causes. No temporary fixes. Senior developer standards.
- **Minimal Impact**: Changes should only touch what's necessary. Avoid introducing bugs.
