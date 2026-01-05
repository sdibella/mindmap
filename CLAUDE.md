# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a wrapper project for organizing and managing an Obsidian vault. The actual Obsidian vault is stored in the `StefanEternal/` directory, which is excluded from version control.

## Repository Structure

- `StefanEternal/` - The Obsidian vault (gitignored, not version controlled)
- This repository contains tools, scripts, and utilities for organizing the vault

## Vault Organization (PARA Method)

The vault follows the PARA organizational method:

```
StefanEternal/
├── 00 - Inbox/           # Capture zone for new, unprocessed notes
├── 01 - Projects/        # Active projects with specific goals and deadlines
├── 02 - Areas/           # Ongoing areas of responsibility (no end date)
├── 03 - Resources/       # Reference materials, learnings, research
├── 04 - Archives/        # Completed projects and inactive items
├── Templates/            # Note templates for consistent structure
├── Attachments/          # Images, PDFs, and other media files
└── Daily Notes/          # Daily notes (date-based)
```

### Available Templates

Located in `StefanEternal/Templates/`:
- **Daily Note.md** - Daily journaling and task tracking
- **Project.md** - Project planning with goals, timeline, and tasks
- **Meeting Note.md** - Meeting agenda, notes, decisions, and action items
- **Resource.md** - Book notes, article summaries, learning resources
- **Weekly Review.md** - Weekly reflection and planning

## PARA Workflow

1. **Capture** → Everything starts in `00 - Inbox/`
2. **Clarify** → Process inbox items and determine their type:
   - Projects: Has a goal and deadline → `01 - Projects/`
   - Areas: Ongoing responsibility → `02 - Areas/`
   - Resources: Reference material → `03 - Resources/`
3. **Archive** → When projects complete or areas become inactive → `04 - Archives/`

## Working with the Obsidian Vault

- The Obsidian vault files are in `StefanEternal/` but should NOT be committed to git
- Any scripts or tools created should operate on files within `StefanEternal/`
- Obsidian uses markdown files (.md) for notes with YAML frontmatter for metadata
- Links between notes use the `[[Note Name]]` or `[[Note Name|Display Text]]` format
- Templates use Obsidian's template syntax (e.g., `{{date}}`, `{{title}}`)

## Important Notes

- Never remove `StefanEternal/` from .gitignore
- Tools should be read-safe by default - confirm before making bulk modifications to vault files
- Preserve existing note structure and formatting when processing vault files
