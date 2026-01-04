# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a wrapper project for organizing and managing an Obsidian vault. The actual Obsidian vault is stored in the `StefanEternal/` directory, which is excluded from version control.

## Repository Structure

- `StefanEternal/` - The Obsidian vault (gitignored, not version controlled)
- This repository contains tools, scripts, and utilities for organizing the vault

## Working with the Obsidian Vault

- The Obsidian vault files are in `StefanEternal/` but should NOT be committed to git
- Any scripts or tools created should operate on files within `StefanEternal/`
- Obsidian uses markdown files (.md) for notes with YAML frontmatter for metadata
- Links between notes use the `[[Note Name]]` or `[[Note Name|Display Text]]` format

## Important Notes

- Never remove `StefanEternal/` from .gitignore
- Tools should be read-safe by default - confirm before making bulk modifications to vault files
- Preserve existing note structure and formatting when processing vault files
