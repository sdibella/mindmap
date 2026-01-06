#!/bin/bash
# Claude Code Skill: Process Tweet Screenshots
# Add this to your Claude Code skills to enable /process-tweets command

cd "$(dirname "$0")"
node process-tweets.js "$@"
