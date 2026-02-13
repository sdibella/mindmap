---
title: OPENCLAW Automation Setup Guide
version: 1.0
updated: 2026-02-13
---

# OPENCLAW Automation Setup Guide

**Purpose:** Configure automated nightly/weekly/monthly vault intelligence processes

**Audience:** Stefan (setup + monitoring)

---

## Quick Start (5 minutes)

### 1. Make Scripts Executable

```bash
cd /Users/gw/Workspace/mindmap/scripts/tweet-processor

chmod +x vault-intelligence-engine.py
chmod +x weekly-review.py
chmod +x monthly-synthesis.py
```

### 2. Test the Scripts

```bash
# Test nightly engine
python3 vault-intelligence-engine.py --report

# Test weekly review
python3 weekly-review.py

# Test monthly synthesis
python3 monthly-synthesis.py
```

### 3. Set Up Cron Jobs

Edit your crontab:

```bash
crontab -e
```

Add these three lines:

```cron
# OPENCLAW Vault Intelligence - Nightly (2 AM)
0 2 * * * cd /Users/gw/Workspace/mindmap/scripts/tweet-processor && python3 vault-intelligence-engine.py --report > /tmp/openclaw-nightly.log 2>&1

# OPENCLAW Vault Intelligence - Weekly Review (Monday 8 AM)
0 8 * * 1 cd /Users/gw/Workspace/mindmap/scripts/tweet-processor && python3 weekly-review.py >> /tmp/openclaw-weekly.log 2>&1

# OPENCLAW Vault Intelligence - Monthly Synthesis (1st of month, 9 AM)
0 9 1 * * cd /Users/gw/Workspace/mindmap/scripts/tweet-processor && python3 monthly-synthesis.py >> /tmp/openclaw-monthly.log 2>&1
```

### 4. Verify Cron Setup

```bash
# Check installed cron jobs
crontab -l

# Monitor logs
tail -f /tmp/openclaw-nightly.log
tail -f /tmp/openclaw-weekly.log
tail -f /tmp/openclaw-monthly.log
```

---

## Detailed Setup

### File Locations Reference

```
/Users/gw/Workspace/mindmap/
├── docs/
│   ├── OPENCLAW_VAULT_INTELLIGENCE_PROTOCOL.md    (Master protocol)
│   ├── OPENCLAW_AUTOMATION_SETUP.md                (This file)
│   └── syntheses/                                  (Monthly reports)
│       └── MONTHLY_SYNTHESIS_2026_02.md
│
├── scripts/tweet-processor/
│   ├── vault-intelligence-engine.py                (Nightly)
│   ├── weekly-review.py                            (Weekly)
│   ├── monthly-synthesis.py                        (Monthly)
│   ├── vault-metadata.json                         (Generated nightly)
│   └── WEEKLY_REVIEW.md                            (Generated weekly)
│
└── StefanEternal/
    ├── atoms/                                      (Content to analyze)
    ├── maps/                                       (MOC files)
    ├── 00 - Inbox/
    ├── 01 - Projects/
    └── ... other folders
```

### Vault Path

The system scans: `/Users/gw/Workspace/mindmap/StefanEternal`

To use a different vault, modify cron commands:

```bash
python3 vault-intelligence-engine.py --vault /path/to/vault --report
```

### Output Locations

**Nightly:**
- Metadata: `scripts/tweet-processor/vault-metadata.json`
- Log: `/tmp/openclaw-nightly.log`

**Weekly:**
- Review: `scripts/tweet-processor/WEEKLY_REVIEW.md`
- Log: `/tmp/openclaw-weekly.log`

**Monthly:**
- Synthesis: `scripts/tweet-processor/MONTHLY_SYNTHESIS.md`
- Archived to: `docs/syntheses/MONTHLY_SYNTHESIS_YYYY_MM.md`
- Log: `/tmp/openclaw-monthly.log`

---

## Nightly Process (Autonomous)

**Schedule:** 2:00 AM daily
**Duration:** 2-3 minutes
**Output:** vault-metadata.json

### What Happens

```
1. Scan all markdown files in StefanEternal/
2. Apply OPENCLAW_VAULT_INTELLIGENCE_PROTOCOL.md rules
3. Categorize each file (primary + secondary tags)
4. Calculate similarity scores between all files
5. Generate backlink recommendations
6. Save metadata to vault-metadata.json
7. Generate console report (saved to log)
```

### Manual Run

```bash
cd /Users/gw/Workspace/mindmap/scripts/tweet-processor

# Full analysis with report
python3 vault-intelligence-engine.py --report

# Validation only (check without modifying)
python3 vault-intelligence-engine.py --mode validate

# Custom vault path
python3 vault-intelligence-engine.py --vault /path/to/vault --report
```

### Expected Output

```
======================================================================
🤖 OPENCLAW VAULT INTELLIGENCE ENGINE
======================================================================

📖 Scanning vault at /Users/gw/Workspace/mindmap/StefanEternal...
✅ Scanned 266 files
🔗 Calculating relationships...
  Progress: 50/266
  Progress: 100/266
  ... etc

✅ Intelligence engine complete!
📁 Metadata saved to: vault-metadata.json

======================================================================
📊 CATEGORIZATION REPORT
======================================================================

📈 Coverage:
  Total files: 266
  Files with categories: 260 (97.7%)
  Files with secondary tags: 180 (67.7%)

🎯 Confidence:
  High (≥0.85): 240
  Low (<0.65): 8

🔗 Relationships:
  Strong links: 1,260
  Medium links: 1,448

🏷️  Category Distribution:
  software-development: 81
  ai-models-research: 69
  learning-resources: 67
  ... etc
```

---

## Weekly Process (Interactive)

**Schedule:** Monday 8:00 AM
**Duration:** 1-2 minutes
**Output:** WEEKLY_REVIEW.md

### What Happens

```
1. Load metadata from vault-intelligence-engine.py
2. Identify low-confidence categorizations
3. Find uncategorized files
4. Detect edge cases and anomalies
5. Identify emerging category patterns
6. Generate markdown review report
```

### Review Report Contents

- ⚠️ Low confidence items (for your review)
- 🔍 Uncategorized files
- 🎯 Edge cases and anomalies
- 💡 Emerging patterns and trends
- 🎓 Suggestions for improvement

### Manual Run

```bash
python3 weekly-review.py

# Output: WEEKLY_REVIEW.md
# Review this file for items needing attention
```

### What To Do With It

1. **Open** `WEEKLY_REVIEW.md`
2. **Review** low-confidence items
3. **Provide feedback** (mentally or in comments)
4. **Note patterns** you find interesting
5. **Store** for monthly synthesis

---

## Monthly Process (Deep Learning)

**Schedule:** 1st of month, 9:00 AM
**Duration:** 2-3 minutes
**Output:** MONTHLY_SYNTHESIS.md

### What Happens

```
1. Load metadata from entire month of nightly runs
2. Analyze category coverage and distribution
3. Calculate confidence score trends
4. Identify hub atoms (most connected)
5. Detect emerging patterns
6. Propose protocol updates
7. Generate executive summary report
```

### Synthesis Report Contents

- 📊 Category distribution analysis
- 🎯 Confidence analysis (high/medium/low breakdown)
- 🔗 Relationship insights and hub atoms
- 💡 Emerging patterns worth investigating
- 🎓 Recommendations for next month
- 📋 Proposed protocol updates

### Manual Run

```bash
python3 monthly-synthesis.py

# Output: MONTHLY_SYNTHESIS.md
# This becomes your monthly intelligence report
```

### Monthly Workflow

1. **Receive** automated MONTHLY_SYNTHESIS.md
2. **Review** findings and recommendations
3. **Approve** or modify proposed protocol updates
4. **Update** OPENCLAW_VAULT_INTELLIGENCE_PROTOCOL.md
5. **Archive** synthesis to docs/syntheses/MONTHLY_SYNTHESIS_YYYY_MM.md
6. **Notify** system of updates
7. **Continue** to next month

---

## Cron Job Details

### Time Zones

The times above are in your local timezone. Adjust as needed:

```bash
# 2 AM local time: 0 2 * * *
# 8 AM Monday: 0 8 * * 1
# 9 AM on 1st: 0 9 1 * *
```

### Cron Syntax Reference

```
┌───────────── minute (0-59)
│ ┌───────────── hour (0-23)
│ │ ┌───────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12)
│ │ │ │ ┌───────────── day of week (0-7) (0 and 7 are Sunday)
│ │ │ │ │
│ │ │ │ │
0 2 * * *    (Every day at 2:00 AM)
0 8 * * 1    (Every Monday at 8:00 AM)
0 9 1 * *    (1st of month at 9:00 AM)
```

### Environment

Make sure Python 3.6+ is available in your PATH:

```bash
# Check
which python3
python3 --version

# If needed, add to cron (full path):
/usr/local/bin/python3 vault-intelligence-engine.py
```

---

## Monitoring & Troubleshooting

### Check if Cron is Running

```bash
# View log files
tail -50 /tmp/openclaw-nightly.log
tail -50 /tmp/openclaw-weekly.log
tail -50 /tmp/openclaw-monthly.log

# Check system cron logs (macOS)
log stream --predicate 'process == "cron"' --level debug

# Check if Python process ran
ps aux | grep vault-intelligence
```

### Verify Metadata Is Being Generated

```bash
ls -lah /Users/gw/Workspace/mindmap/scripts/tweet-processor/vault-metadata.json

# Should be recent (updated daily)
stat vault-metadata.json
```

### Test Manually Before Relying on Cron

```bash
# Run each script manually to verify
cd /Users/gw/Workspace/mindmap/scripts/tweet-processor

python3 vault-intelligence-engine.py --report
echo "---"
python3 weekly-review.py
echo "---"
python3 monthly-synthesis.py
```

### Common Issues

**Issue:** "command not found: python3"
- **Solution:** Use full path in cron: `/usr/local/bin/python3`
- **Check:** `which python3` to find correct path

**Issue:** Metadata file not updating
- **Solution:** Check cron logs, verify script runs manually
- **Check:** `tail -f /tmp/openclaw-nightly.log`

**Issue:** "No such file or directory: vault-metadata.json"
- **Solution:** Ensure nightly job runs first, or run weekly from correct directory
- **Check:** `cd /Users/gw/Workspace/mindmap/scripts/tweet-processor` before running weekly/monthly

**Issue:** Low confidence items appear every week
- **Solution:** Update OPENCLAW_VAULT_INTELLIGENCE_PROTOCOL.md with new patterns
- **Check:** Monthly synthesis report for recommendations

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     NIGHTLY (2 AM)                          │
│  vault-intelligence-engine.py --report                      │
│                                                              │
│  Inputs: StefanEternal/atoms/** (all markdown files)       │
│  Process: Categorize + analyze similarity + backlinks      │
│  Output: vault-metadata.json                               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ (metadata fed to weekly)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    WEEKLY (8 AM Monday)                     │
│  weekly-review.py                                           │
│                                                              │
│  Input: vault-metadata.json                                │
│  Process: Surface anomalies & patterns                     │
│  Output: WEEKLY_REVIEW.md                                  │
│                                                              │
│  👁️  REVIEW THIS - Low confidence items, edge cases        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ (feedback informs monthly)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                MONTHLY (9 AM, 1st of month)                │
│  monthly-synthesis.py                                      │
│                                                              │
│  Input: vault-metadata.json + all weekly reviews          │
│  Process: Deep analysis + learning + evolution             │
│  Output: MONTHLY_SYNTHESIS.md                              │
│                                                              │
│  ⚡ PROPOSES UPDATES to OPENCLAW_VAULT_INTELLIGENCE_...    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ (you approve updates)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│           UPDATE PROTOCOL (Manual - Stefan)                │
│                                                              │
│  Edit: OPENCLAW_VAULT_INTELLIGENCE_PROTOCOL.md             │
│  - Merge/clarify categories                               │
│  - Update patterns based on findings                      │
│  - Add new secondary tags                                 │
│  - Document changes in Evolution Log                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ (new protocol fed to next nightly)
                         ▼
           ┌──────────────────────────────┐
           │ NIGHTLY CYCLE REPEATS        │
           │ (with updated protocol)      │
           └──────────────────────────────┘
```

---

## Performance Notes

### Expected Runtime

- **Nightly:** 2-3 minutes (depends on number of files)
- **Weekly:** 1-2 minutes (reads existing metadata)
- **Monthly:** 2-3 minutes (same as nightly + analysis)

### Resource Usage

- CPU: Low (Python script, single-threaded)
- Memory: ~50-100 MB
- Disk: ~100 KB metadata + logs

### Optimization

If you have 1000+ files and it's too slow:
- Reduce similarity scoring threshold (fewer comparisons)
- Run monthly instead of nightly
- Implement caching between runs

---

## Archiving & Reporting

### Monthly Archives

```bash
# Monthly syntheses are saved to:
docs/syntheses/MONTHLY_SYNTHESIS_2026_02.md
docs/syntheses/MONTHLY_SYNTHESIS_2026_03.md
docs/syntheses/MONTHLY_SYNTHESIS_2026_04.md
# ... etc
```

### Viewing Archives

```bash
# List all monthly syntheses
ls -lah /Users/gw/Workspace/mindmap/docs/syntheses/

# View a specific month
cat /Users/gw/Workspace/mindmap/docs/syntheses/MONTHLY_SYNTHESIS_2026_02.md
```

### Trend Analysis

Compare monthly syntheses over time to see:
- Category distribution changes
- Confidence score improvements
- New patterns emerging
- System evolution

---

## Customization

### Change Schedule

Edit crontab and modify times:

```bash
# Example: Move nightly to 3 AM instead of 2 AM
0 3 * * * ...

# Example: Weekly review on Friday instead of Monday
0 8 * * 5 ...
```

### Change Vault Path

Modify cron command:

```bash
python3 vault-intelligence-engine.py --vault /different/vault/path
```

### Change Output Locations

Modify script calls:

```bash
python3 vault-intelligence-engine.py --output /custom/path/metadata.json
python3 weekly-review.py --output /custom/path/WEEKLY_REVIEW.md
python3 monthly-synthesis.py --output /custom/path/MONTHLY_SYNTHESIS.md
```

---

## Emergency Procedures

### Skip a Scheduled Run

```bash
# Temporarily disable in crontab
crontab -e
# Comment out the line with #
# 0 2 * * * cd ... (commented out - won't run)
```

### Manual Run if Automated Fails

```bash
cd /Users/gw/Workspace/mindmap/scripts/tweet-processor

# Run manually
python3 vault-intelligence-engine.py --report

# Check output
cat vault-metadata.json | head -100
```

### Reset to Clean State

```bash
# Remove old metadata
rm vault-metadata.json WEEKLY_REVIEW.md MONTHLY_SYNTHESIS.md

# Re-run nightly engine
python3 vault-intelligence-engine.py --report
```

---

## Support & Questions

### Key Files to Reference

- Protocol: `docs/OPENCLAW_VAULT_INTELLIGENCE_PROTOCOL.md`
- This guide: `docs/OPENCLAW_AUTOMATION_SETUP.md`
- Recent synthesis: `scripts/tweet-processor/MONTHLY_SYNTHESIS.md`

### What to Check When Something Breaks

1. ✅ Cron job is configured: `crontab -l`
2. ✅ Scripts are executable: `ls -la vault-intelligence-*.py`
3. ✅ Python works: `python3 --version`
4. ✅ Vault path exists: `ls -la /Users/gw/Workspace/mindmap/StefanEternal`
5. ✅ Recent logs: `tail -50 /tmp/openclaw-*.log`

---

**Last Updated:** 2026-02-13
**Next Review:** When system is deployed and running
