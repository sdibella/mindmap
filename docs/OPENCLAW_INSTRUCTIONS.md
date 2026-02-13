---
title: OPENCLAW Vault Intelligence - Implementation Instructions
audience: OPENCLAW AI Assistant
version: 1.0
---

# OPENCLAW: Vault Intelligence Routine

## Your Mission

Continuously maintain and evolve the StefanEternal knowledge vault through intelligent categorization, backlinking, and learning.

**Schedule:**
- **Nightly (2 AM):** Categorize and analyze all vault content
- **Weekly (8 AM Monday):** Surface anomalies and patterns for review
- **Monthly (9 AM, 1st):** Deep analysis and propose protocol updates

---

## Quick Setup (Copy & Paste)

### 1. Verify Scripts Exist

```bash
ls -la /Users/gw/Workspace/mindmap/scripts/tweet-processor/vault-intelligence-engine.py
ls -la /Users/gw/Workspace/mindmap/scripts/tweet-processor/weekly-review.py
ls -la /Users/gw/Workspace/mindmap/scripts/tweet-processor/monthly-synthesis.py
```

### 2. Make Executable

```bash
cd /Users/gw/Workspace/mindmap/scripts/tweet-processor
chmod +x vault-intelligence-engine.py weekly-review.py monthly-synthesis.py
```

### 3. Install Cron Jobs

```bash
crontab -e
```

Paste these three lines:

```cron
# OPENCLAW Nightly - 2 AM
0 2 * * * cd /Users/gw/Workspace/mindmap/scripts/tweet-processor && python3 vault-intelligence-engine.py --report > /tmp/openclaw-nightly.log 2>&1

# OPENCLAW Weekly Review - Monday 8 AM
0 8 * * 1 cd /Users/gw/Workspace/mindmap/scripts/tweet-processor && python3 weekly-review.py >> /tmp/openclaw-weekly.log 2>&1

# OPENCLAW Monthly Synthesis - 1st of month 9 AM
0 9 1 * * cd /Users/gw/Workspace/mindmap/scripts/tweet-processor && python3 monthly-synthesis.py >> /tmp/openclaw-monthly.log 2>&1
```

Save and exit.

### 4. Verify Installation

```bash
crontab -l  # Should show your 3 new entries
```

### 5. Test Each Script

```bash
cd /Users/gw/Workspace/mindmap/scripts/tweet-processor

# Test nightly
python3 vault-intelligence-engine.py --report

# Test weekly
python3 weekly-review.py

# Test monthly
python3 monthly-synthesis.py
```

---

## Your Responsibilities

### Every Night (Automated)

`vault-intelligence-engine.py` runs at 2 AM:
- ✅ Scans all markdown files in StefanEternal/
- ✅ Applies OPENCLAW_VAULT_INTELLIGENCE_PROTOCOL.md rules
- ✅ Categorizes each file (primary + secondary tags)
- ✅ Calculates similarity scores and backlinks
- ✅ Saves metadata to `vault-metadata.json`
- ✅ Logs to `/tmp/openclaw-nightly.log`

**You should:** Monitor the log occasionally. If it fails, check `/tmp/openclaw-nightly.log`.

### Every Monday 8 AM (Automated)

`weekly-review.py` runs every Monday:
- ✅ Loads metadata from nightly run
- ✅ Identifies low-confidence categorizations
- ✅ Detects edge cases and anomalies
- ✅ Identifies emerging patterns
- ✅ Generates `WEEKLY_REVIEW.md`

**You should:** Read the WEEKLY_REVIEW.md and note items that need attention. These feed into monthly analysis.

### 1st of Month at 9 AM (Automated)

`monthly-synthesis.py` runs on the 1st:
- ✅ Analyzes month of categorization data
- ✅ Identifies hubs, isolated atoms, patterns
- ✅ Calculates trend metrics
- ✅ Proposes protocol updates
- ✅ Generates `MONTHLY_SYNTHESIS.md`

**You should:**
1. Read `MONTHLY_SYNTHESIS.md`
2. Review proposed protocol updates
3. Update `docs/OPENCLAW_VAULT_INTELLIGENCE_PROTOCOL.md` with approved changes
4. Increment version number in protocol
5. Archive synthesis to `docs/syntheses/MONTHLY_SYNTHESIS_YYYY_MM.md`
6. Continue to next month

---

## File Reference

### Master Documents (Read These)

- **Protocol:** `/Users/gw/Workspace/mindmap/docs/OPENCLAW_VAULT_INTELLIGENCE_PROTOCOL.md`
  - Complete categorization rules and backlinking strategy
  - Authority for all decisions
  - Updated monthly with learnings

- **Automation:** `/Users/gw/Workspace/mindmap/docs/OPENCLAW_AUTOMATION_SETUP.md`
  - Detailed cron setup instructions
  - Troubleshooting guide
  - Performance notes

### Scripts (Automated)

- **Nightly:** `scripts/tweet-processor/vault-intelligence-engine.py`
- **Weekly:** `scripts/tweet-processor/weekly-review.py`
- **Monthly:** `scripts/tweet-processor/monthly-synthesis.py`

### Generated Files (In Working Directory)

- **Nightly output:** `vault-metadata.json` (reference for weekly/monthly)
- **Weekly output:** `WEEKLY_REVIEW.md` (review this!)
- **Monthly output:** `MONTHLY_SYNTHESIS.md` (review and approve updates)
- **Logs:** `/tmp/openclaw-nightly.log`, `/tmp/openclaw-weekly.log`, `/tmp/openclaw-monthly.log`

### Archives

- **Monthly syntheses:** `docs/syntheses/MONTHLY_SYNTHESIS_YYYY_MM.md`

---

## Monitoring

### Daily Check (30 seconds)

```bash
# Check nightly completed
ls -lah /Users/gw/Workspace/mindmap/scripts/tweet-processor/vault-metadata.json

# Quick log check
tail -10 /tmp/openclaw-nightly.log
```

### Weekly Check (5 minutes)

```bash
# Read this file
cat /Users/gw/Workspace/mindmap/scripts/tweet-processor/WEEKLY_REVIEW.md

# Note any items needing attention
```

### Monthly Check (15 minutes)

```bash
# Read synthesis
cat /Users/gw/Workspace/mindmap/scripts/tweet-processor/MONTHLY_SYNTHESIS.md

# Approve/modify protocol updates
vim /Users/gw/Workspace/mindmap/docs/OPENCLAW_VAULT_INTELLIGENCE_PROTOCOL.md

# Update version and evolution log
# Archive synthesis
mkdir -p /Users/gw/Workspace/mindmap/docs/syntheses
cp /Users/gw/Workspace/mindmap/scripts/tweet-processor/MONTHLY_SYNTHESIS.md \
   /Users/gw/Workspace/mindmap/docs/syntheses/MONTHLY_SYNTHESIS_$(date +%Y_%m).md
```

---

## Troubleshooting

### "Script failed to run"

```bash
# 1. Check script exists and is executable
ls -la /Users/gw/Workspace/mindmap/scripts/tweet-processor/*.py

# 2. Check Python is available
which python3
python3 --version

# 3. Run manually to see error
cd /Users/gw/Workspace/mindmap/scripts/tweet-processor
python3 vault-intelligence-engine.py --report
```

### "vault-metadata.json not found"

```bash
# Run nightly engine first
cd /Users/gw/Workspace/mindmap/scripts/tweet-processor
python3 vault-intelligence-engine.py

# Then run weekly
python3 weekly-review.py
```

### "Cron not running"

```bash
# Check if installed
crontab -l

# Check system logs (macOS)
log stream --predicate 'process == "cron"'

# Try manual run
cd /Users/gw/Workspace/mindmap/scripts/tweet-processor
python3 vault-intelligence-engine.py
```

---

## Decision Points

### When Low Confidence Items Appear (Weekly)

Review `WEEKLY_REVIEW.md`:
- **If legitimate edge case:** Document in protocol
- **If miscategorized:** Manually correct and note pattern
- **If new category needed:** Flag for monthly synthesis

### When Emerging Patterns Appear (Monthly)

Review `MONTHLY_SYNTHESIS.md`:
- **Patterns suggest new category:** Add to protocol
- **Patterns suggest merge:** Consolidate categories
- **Patterns suggest clarification:** Update regex patterns
- **Nothing changed:** Continue as-is

### When Protocol Updates Proposed (Monthly)

1. **Review** proposal in MONTHLY_SYNTHESIS.md
2. **Approve** by editing OPENCLAW_VAULT_INTELLIGENCE_PROTOCOL.md
3. **Record** change in "Evolution Log" section
4. **Increment** version number
5. **Save** and new nightly will use updated rules

---

## Success Criteria

✅ **Nightly runs consistently** - No failed runs (check logs weekly)
✅ **Weekly reviews surface insights** - Patterns become visible
✅ **Monthly updates improve protocol** - System gets better each month
✅ **Vault stays organized** - Files properly categorized
✅ **Backlinks are meaningful** - Related content connects naturally
✅ **You understand everything** - Protocol and findings make sense

---

## Commands Reference

```bash
# View logs
tail -50 /tmp/openclaw-nightly.log
tail -50 /tmp/openclaw-weekly.log
tail -50 /tmp/openclaw-monthly.log

# Run manually
cd /Users/gw/Workspace/mindmap/scripts/tweet-processor
python3 vault-intelligence-engine.py --report
python3 weekly-review.py
python3 monthly-synthesis.py

# Check cron
crontab -l

# Edit cron
crontab -e

# View outputs
cat vault-metadata.json | head -50
cat WEEKLY_REVIEW.md
cat MONTHLY_SYNTHESIS.md

# Archive monthly
cp MONTHLY_SYNTHESIS.md docs/syntheses/MONTHLY_SYNTHESIS_$(date +%Y_%m).md
```

---

## Questions?

**Where do I find the rules?**
→ `docs/OPENCLAW_VAULT_INTELLIGENCE_PROTOCOL.md`

**How do I set this up?**
→ Follow "Quick Setup" above, or detailed guide in `docs/OPENCLAW_AUTOMATION_SETUP.md`

**What if something breaks?**
→ See "Troubleshooting" section above

**How do I know if it's working?**
→ Check recent `vault-metadata.json` and logs in `/tmp/`

**Can I change the schedule?**
→ Yes, edit crontab with new times (see OPENCLAW_AUTOMATION_SETUP.md)

---

## Next Steps

1. ✅ Run Quick Setup above
2. ✅ Test each script manually
3. ✅ Verify cron installation (`crontab -l`)
4. ✅ Wait for first nightly run (2 AM)
5. ✅ Review first weekly report (Monday 8 AM)
6. ✅ Approve first monthly synthesis (next month 1st, 9 AM)
7. ✅ Continue monthly protocol updates

---

**Status:** Ready for deployment
**Version:** 1.0
**Last Updated:** 2026-02-13
**Created by:** Claude
**For:** Stefan's StefanEternal vault intelligence system
