---
title: OPENCLAW Vault Intelligence Protocol
version: 1.0
updated: 2026-02-13
status: living_document
---

# OPENCLAW Vault Intelligence Protocol

**Purpose:** Authoritative guide for intelligent categorization, backlinking, and continuous learning of all content in StefanEternal knowledge vault.

**Audience:** OPENCLAW AI assistant (primary), Stefan (for monthly review)

**Update Schedule:** Monthly synthesis + learning (see end of document)

---

## Table of Contents

1. [System Philosophy](#system-philosophy)
2. [The 10 Primary Categories](#the-10-primary-categories)
3. [Secondary Tags](#secondary-tags)
4. [Categorization Rules](#categorization-rules)
5. [Backlinking Strategy](#backlinking-strategy)
6. [Edge Cases & Decision Trees](#edge-cases--decision-trees)
7. [Confidence Scoring](#confidence-scoring)
8. [Monthly Evolution & Learning](#monthly-evolution--learning)
9. [Implementation Reference](#implementation-reference)

---

## System Philosophy

### Goals

1. **Intelligent Discoverability** - Every piece of content connects to related material
2. **Continuous Evolution** - System learns from data patterns and user feedback
3. **Balanced Autonomy** - Mostly automatic, human input on edge cases
4. **Knowledge Preservation** - Track what changed and why (audit trail)

### Core Principle

**Categorization drives backlinking.** Better tags → better relationships → better graph.

The system is never "done" — it improves monthly as patterns emerge and knowledge grows.

---

## The 10 Primary Categories

Use these regex patterns to identify which categories apply to content. **Tag ALL that match** (multi-tag is the default).

### 1. **ai-agents** 🤖
**Focus:** Building and orchestrating autonomous agents, multi-agent systems, agent frameworks

**Patterns:**
```
\bagent\b
\bagentic\b
\bautonomous\s+system
\borchestr
\bmulti-?agent
\bworkflow\s+automation
\btask\s+automation
```

**Examples:** agent-automation.md, agent-native-software-design.md

**Confidence markers:**
- High: Multiple agent-specific terms
- Medium: Single mention of agent concepts
- Low: "Agent" used in non-technical context (e.g., real estate agent)

---

### 2. **prediction-markets** 🎯
**Focus:** Prediction markets, weather betting, event forecasting, Polymarket/Kalshi strategies

**Patterns:**
```
polymarket
kalshi
prediction\s+market
\bforecast(ing)?
weather\s+bot
event\s+betting
```

**Examples:** polymarket-strategy.md, weather-trading-guide.md

**Confidence markers:**
- High: Specific platform names (Polymarket, Kalshi)
- Medium: General prediction market discussion
- Low: "Predict" in non-market context

---

### 3. **crypto-defi** ₿
**Focus:** Blockchain, DeFi protocols, smart contracts, crypto trading, NFTs, DAOs

**Patterns:**
```
\bcrypto\b
\bblockchain\b
bitcoin
ethereum
\bdefi\b
\bdao\b
\bnft\b
smart\s+contract
yield\s+farming
```

**Examples:** defi-strategy.md, blockchain-architecture.md

**Confidence markers:**
- High: Multiple crypto-specific terms
- Medium: One category (e.g., only mentions Bitcoin)
- Low: "Block" used in non-blockchain context

---

### 4. **software-development** 💻
**Focus:** Code, APIs, SDKs, programming frameworks, development tools, infrastructure

**Patterns:**
```
\bcode\b
\bprogramming\b
\bsdk\b
\bapi\b
\bgithub\b
python
javascript
typescript
react
\bframework\b
\blibrary\b
```

**Examples:** api-guide.md, python-tutorial.md

**Confidence markers:**
- High: Code examples or specific language names
- Medium: General programming discussion
- Low: "Code" used metaphorically

---

### 5. **ai-models-research** 🧠
**Focus:** LLMs, model training, inference optimization, AI infrastructure, benchmarks, research

**Patterns:**
```
\bllm\b
large\s+language\s+model
\bmachine\s+learning\b
\bneural\s+network
\bmodel\s+training
\binference
\bgpu\b
anthropic
openai
claude
gemini
```

**Examples:** llm-benchmarks.md, inference-optimization.md

**Confidence markers:**
- High: Technical model concepts or specific model names
- Medium: General AI discussion
- Low: "Learning" in non-ML context

---

### 6. **stock-trading-finance** 📈
**Focus:** Stock trading, dividend strategies, portfolio management, technical analysis

**Patterns:**
```
\bstock\b
\bportfolio\b
\bdividend
\bswing\s+trade
\btechnical\s+analysis
\btrading\s+strategy
\bmarket\s+analysis
\bequity\b
```

**Examples:** stock-predictions.md, dividend-strategy.md

**Confidence markers:**
- High: Specific trading strategies or stock examples
- Medium: General financial discussion
- Low: "Market" without trading context

---

### 7. **business-entrepreneurship** 🚀
**Focus:** Startups, business models, growth strategies, founder stories, marketing

**Patterns:**
```
\bstartup\b
\bentrepreneur
\bfounder
\bbusiness\s+model
\bgrowth\s+strategy
\bsaas\b
\bproduct-?market\s+fit
\bfundraising
\bmarketing
```

**Examples:** founder-story.md, business-model-analysis.md

**Confidence markers:**
- High: Specific business concepts or founder context
- Medium: General business discussion
- Low: "Business" used generically

---

### 8. **systems-architecture** 🏛️
**Focus:** System design, scalability, infrastructure design, design patterns, distributed systems

**Patterns:**
```
\barchitecture\b
\bsystem\s+design
\bscalability
\binfrastructure
\bdesign\s+pattern
\bdistributed\s+system
\bmicroservice
```

**Examples:** system-design-patterns.md, scalability-guide.md

**Confidence markers:**
- High: Technical architecture concepts
- Medium: Single architecture mention
- Low: "Design" in non-technical context

---

### 9. **learning-resources** 📚
**Focus:** How-to guides, tutorials, blueprints, roadmaps, educational frameworks, courses

**Patterns:**
```
\bguide\b
\btutorial\b
\bhow\s+to
\bhow-?to
\broadmap\b
\bcourse\b
\bblueprint\b
\bstep-?by-?step
\bframework\b
```

**Examples:** tutorial.md, roadmap.md, 100000-on-copy-trading-blueprint.md

**Confidence markers:**
- High: Multiple educational keywords
- Medium: Structured guide format
- Low: "Guide" used metaphorically

---

### 10. **people-personas** 👤
**Focus:** Individual profiles, founder/creator insights, personality-driven content

**Detection Rules:**
- File is named after a person (e.g., `ben-tossell.md`, `adam-robinson.md`)
- Content is primarily about someone's views, story, or perspective
- Single-author voice or personal brand focus

**Examples:** ben-tossell.md, kyle-the-writer.md

**Confidence markers:**
- High: File named after person + content about them
- Medium: Discussion of person's ideas
- Low: Passing mention of person

**Important:** Combine with topic tags
- If Ben Tossell talks about AI: `people-personas, ai-agents, software-development`
- This enables: "Show me everything about AI people" AND "Show me all AI content"

---

## Secondary Tags

Add alongside primary tags to capture nuance and learning context:

| Tag | When to Use | Example |
|-----|------------|---------|
| **ai-native** | Content specifically designed for AI/agent consumption | Prompt templates, agent system prompts |
| **practical-strategy** | Step-by-step actionable frameworks (not theoretical) | Trading blueprints, implementation guides |
| **research-based** | Academic papers, benchmarks, research findings | Performance analysis, comparative studies |
| **case-study** | Real-world examples and success stories | "How I made $100k with..." |
| **tool-recommendation** | Specific product/tool recommendations | "Best tools for X" |
| **contrarian** | Unconventional or challenging viewpoints | "Why everyone's wrong about..." |
| **migrated** | Source tracking (from old system) | Keep for audit trail |
| **tweet** | Source tracking (from tweet import) | Keep for audit trail |

**Example:**
```yaml
tags: [prediction-markets, ai-agents, practical-strategy, case-study]
```
*"This covers prediction markets + agents + includes actionable steps + real example"*

---

## Categorization Rules

### Rule 1: Multi-Topic Content
**Always include ALL primary categories that represent ≥20% of content**

Example: `polymarket-weather-bot-strategy.md`
- 40% prediction markets content
- 40% ai-agents (bot orchestration)
- 20% learning-resources (tutorial format)

✅ **Tag:** `prediction-markets, ai-agents, learning-resources`
❌ **Don't:** Pick only "the most important one"

### Rule 2: People + Topics
**Use `people-personas` PLUS topic tags**

Example: `ben-tossell.md` (founder who builds AI tools)
- Primary: founder profile → `people-personas`
- Secondary topics: AI tools → `ai-agents, software-development`

✅ **Tag:** `people-personas, ai-agents, software-development`
❌ **Don't:** Only `people-personas`

### Rule 3: Overlapping Content
**Use primary tags + specific secondary tags**

Example: "AI for predicting stock prices"
- 40% AI models
- 40% stock trading
- 20% practical how-to

✅ **Tag:** `ai-models-research, stock-trading-finance, practical-strategy`

### Rule 4: Tangential Mentions
**Don't tag unless category is ≥20% of content**

Example: Startup article mentions "I use ChatGPT for marketing"
- This is 1% of content, not 20%

✅ **Tag:** `business-entrepreneurship` only
❌ **Don't:** Add `ai-models-research`

### Rule 5: Retiring Generic Tags
**Never use generic `ai` tag. Replace with:**
- `ai-agents` (building/orchestrating agents)
- `ai-models-research` (LLMs, models, training)
- `software-development` (using AI APIs/SDKs)

Choose based on context.

---

## Backlinking Strategy

### Goal
Create a knowledge graph where related content naturally connects.

### Algorithm

**Phase 1: Calculate Similarity Scores**
For each pair of files:
- Tag overlap (40% weight): 3+ shared tags → 0.9, 2 shared → 0.7, 1 shared → 0.4
- Keyword matching (30% weight): Extract top 10 keywords, count overlap
- Category clustering (20% weight): Same primary category → 0.7
- Author connection (10% weight): Same author → 0.5

Combined score = weighted average

**Phase 2: Threshold & Classify**
- **Strong (≥0.65):** Add to `## Related Atoms`
- **Medium (0.50-0.64):** Add to `## See Also` with description
- **Weak (<0.50):** Ignore

**Phase 3: Insert Links**
- `## Related Atoms`: Alphabetically sorted peer connections (same category)
- `## See Also`: Medium-relevance + MOC references + descriptions

### Example Output

**Before:**
```markdown
## Related Atoms
- [[placeholder-link]]

## See Also
- [[maps/ai-agents]] — AI-related topics
```

**After:**
```markdown
## Related Atoms
- [[agent-orchestration-patterns]]
- [[polymarket-weather-bot]]
- [[prompt-optimization-guide]]

## See Also
- [[cross-category-ai-finance-hybrid]] — AI + finance intersection
- [[maps/ai-agents]] — AI-related topics
- [[maps/prediction-markets]] — Market forecasting
```

---

## Edge Cases & Decision Trees

### Case 1: File Doesn't Fit Well
**Symptom:** Doesn't match any category pattern clearly

**Decision Tree:**
```
Is it a person? → Add people-personas
Is it 100% reference material? → Add learning-resources
Is it a niche topic (e.g., biohacking)? → Create observation note
Could it spawn a new category? → Flag for monthly review
Otherwise → Leave uncategorized with comment "review-me"
```

### Case 2: Multiple Valid Tags, Hard to Choose
**Symptom:** Content genuinely spans 4+ categories

**Solution:** Tag all of them. This is a feature, not a bug.

Example: "AI agents for prediction markets"
✅ `ai-agents, prediction-markets, ai-models-research, practical-strategy`

### Case 3: Conflicting Categorization Signals
**Symptom:** Title says one thing, content says another

**Rule:** Go by content, not title. First 500 characters of actual content is authoritative.

### Case 4: Very Short Content (< 100 words)
**Rule:** Tag based on title + first sentence only. Flag confidence as LOW.

---

## Confidence Scoring

Every categorization gets a confidence score (0.0 to 1.0):

**Confidence Levels:**
- **HIGH (≥0.85):** Multiple matching patterns, clear category fit
- **MEDIUM (0.65-0.84):** 1-2 matching patterns, some ambiguity
- **LOW (< 0.65):** Single pattern match, vague content, needs review

**Monthly Review:** Surfaces all LOW confidence items for human review.

---

## Monthly Evolution & Learning

### What Happens Each Month

1. **Analysis Phase**
   - Review all low-confidence categorizations
   - Detect new topic clusters emerging
   - Analyze backlinking patterns

2. **Learning Phase**
   - Extract patterns from monthly data
   - Identify new categories or category merges
   - Update confidence thresholds if needed

3. **Proposal Phase**
   - Propose changes to this protocol
   - Present findings to Stefan
   - Record decisions

4. **Update Phase**
   - Update patterns/rules
   - Increment version number
   - Record changes in "Evolution Log" below

5. **Summary Phase**
   - Generate MONTHLY_SYNTHESIS.md
   - Document insights and decisions
   - Archive for future reference

### Evolution Log

| Month | Changes | Reasoning | Files Updated |
|-------|---------|-----------|---|
| 2026-02 | Initial system | New protocol establishment | Protocol v1.0 |
| 2026-03 | TBD | Pending first month of data | - |

---

## Implementation Reference

### How OPENCLAW Uses This

1. **Nightly Run** (`vault-intelligence-engine.py`)
   - Reads this protocol
   - Applies all categorization rules
   - Generates backlinks using similarity algorithm
   - Outputs: `vault-metadata.json`

2. **Weekly Review** (`weekly-review.py`)
   - Identifies LOW confidence items
   - Finds edge cases
   - Detects emerging patterns
   - Outputs: `WEEKLY_REVIEW.md` for Stefan

3. **Monthly Learning** (`monthly-synthesis.py`)
   - Analyzes month of data
   - Proposes protocol updates
   - Updates this document
   - Outputs: `MONTHLY_SYNTHESIS.md`

### Scripts Location
- `scripts/tweet-processor/vault-intelligence-engine.py`
- `scripts/tweet-processor/weekly-review.py`
- `scripts/tweet-processor/monthly-synthesis.py`

### Related Documentation
- `docs/OPENCLAW_AUTOMATION_SETUP.md` — How to run nightly/weekly/monthly
- Monthly syntheses → `docs/syntheses/MONTHLY_SYNTHESIS_YYYY_MM.md`

---

## Questions This Answers

**Q: Why these 10 categories?**
A: Analysis of 266 existing atoms revealed natural topic clusters. These 10 cover 98% of content with minimal overlap.

**Q: What if something doesn't fit?**
A: Flag it with low confidence. Monthly review will determine if we need a new category or if the content is genuinely unique.

**Q: Should I re-tag old content?**
A: Nightly script does this automatically. Monthly review surfaces any that changed significantly.

**Q: What about content that's 50/50 between two categories?**
A: Tag both with equal strength. The backlinking algorithm handles this well.

**Q: How do secondary tags help?**
A: They add context without changing primary categorization. "practical-strategy" helps find actionable guides; "research-based" helps find academic sources.

---

## Next: Automation Setup

See `docs/OPENCLAW_AUTOMATION_SETUP.md` for:
- How to set up nightly cron job
- How to configure weekly review
- How to run monthly synthesis
- Troubleshooting and monitoring

---

**Version:** 1.0 (2026-02-13)
**Status:** Living document - updated monthly
**Last Updated:** 2026-02-13
**Next Review:** 2026-03-13
