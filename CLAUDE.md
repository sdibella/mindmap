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

## Workflow Orchestration

### 1. Plan Mode Default
- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
- If something goes sideways, STOP and re-plan immediately – don't keep pushing
- Use plan mode for verification steps, not just building
- Write detailed specs upfront to reduce ambiguity

### 2. Subagent Strategy
- Use subagents liberally to keep main context window clean
- Offload research, exploration, and parallel analysis to subagents
- For complex problems, throw more compute at it via subagents
- One task per subagent for focused execution

### 3. Self-Improvement Loop
- After ANY correction from the user: update `tasks/lessons.md` with the pattern
- Write rules for yourself that prevent the same mistake
- Ruthlessly iterate on these lessons until mistake rate drops
- Review lessons at session start for relevant project

### 4. Verification Before Done
- Never mark a task complete without proving it works
- Diff behavior between main and your changes when relevant
- Ask yourself: "Would a staff engineer approve this?"
- Run tests, check logs, demonstrate correctness

### 5. Demand Elegance (Balanced)
- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"
- Skip this for simple, obvious fixes – don't over-engineer
- Challenge your own work before presenting it

### 6. Autonomous Bug Fixing
- When given a bug report: just fix it. Don't ask for hand-holding
- Point at logs, errors, failing tests – then resolve them
- Zero context switching required from the user
- Go fix failing CI tests without being told how

## Task Management

1. **Plan First**: Write plan to `tasks/todo.md` with checkable items
2. **Verify Plan**: Check in before starting implementation
3. **Track Progress**: Mark items complete as you go
4. **Explain Changes**: High-level summary at each step
5. **Document Results**: Add review section to `tasks/todo.md`
6. **Capture Lessons**: Update `tasks/lessons.md` after corrections

## Core Principles

- **Simplicity First**: Make every change as simple as possible. Impact minimal code.
- **No Laziness**: Find root causes. No temporary fixes. Senior developer standards.
- **Minimal Impact**: Changes should only touch what's necessary. Avoid introducing bugs.
