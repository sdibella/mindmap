#!/usr/bin/env node

/**
 * Xeet Screenshot Processor
 * Processes X (Twitter) post screenshots using Gemini Flash vision API and creates organized Obsidian notes
 */

const fs = require('fs');
const path = require('path');
const { GoogleGenerativeAI } = require('@google/generative-ai');
require('dotenv').config();

// Configuration
const CONFIG = {
  vaultPath: process.env.VAULT_PATH || path.join(process.env.HOME, 'Library/Mobile Documents/iCloud~md~obsidian/Documents/StefanEternal'),
  screenshotsDir: 'Attachments/Xeets',
  resourcesDir: '03 - Resources/X Insights',
  projectsDir: '01 - Projects/Ideas',
  unsureDir: '00 - Inbox/Xeets to Review',
  logFile: '00 - Inbox/Xeet Processing Log.md',
  processedMarkerFile: '.processed-xeets.json',
  confidenceThreshold: parseFloat(process.env.CONFIDENCE_THRESHOLD) || 0.7,
  aiProvider: process.env.AI_PROVIDER || 'gemini', // 'gemini' or 'claude'
  dryRun: process.argv.includes('--dry-run')
};

// Initialize AI client based on provider
let aiClient;
if (CONFIG.aiProvider === 'gemini') {
  const genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY);
  aiClient = genAI.getGenerativeModel({ model: 'gemini-2.0-flash-exp' });
} else if (CONFIG.aiProvider === 'claude') {
  // For future Claude implementation
  console.log('Claude provider not yet implemented. Please set AI_PROVIDER=gemini');
  process.exit(1);
}

// Track processed screenshots
let processedScreenshots = {};
const processedFile = path.join(__dirname, CONFIG.processedMarkerFile);
if (fs.existsSync(processedFile)) {
  processedScreenshots = JSON.parse(fs.readFileSync(processedFile, 'utf-8'));
}

/**
 * Find new tweet screenshots that haven't been processed
 */
function findNewScreenshots() {
  const screenshotsPath = path.join(CONFIG.vaultPath, CONFIG.screenshotsDir);

  // Create directory if it doesn't exist
  if (!fs.existsSync(screenshotsPath)) {
    console.log(`Creating screenshots directory: ${screenshotsPath}`);
    fs.mkdirSync(screenshotsPath, { recursive: true });
    return [];
  }

  const files = fs.readdirSync(screenshotsPath);
  const imageFiles = files.filter(f =>
    /\.(png|jpg|jpeg)$/i.test(f) && !processedScreenshots[f]
  );

  return imageFiles.map(f => ({
    filename: f,
    fullPath: path.join(screenshotsPath, f),
    relativePath: path.join(CONFIG.screenshotsDir, f)
  }));
}

/**
 * Analyze screenshot using Gemini Vision API
 */
async function analyzeScreenshot(imagePath) {
  console.log(`  Analyzing with ${CONFIG.aiProvider}...`);

  const imageData = fs.readFileSync(imagePath);
  const base64Image = imageData.toString('base64');

  const prompt = `You are analyzing a tweet screenshot to extract and categorize its content for a knowledge management system using the PARA method.

Extract the following information from this tweet screenshot and respond ONLY with valid JSON (no markdown, no code blocks, just raw JSON):

{
  "author": "@username",
  "authorName": "Display Name",
  "date": "approximate date if visible",
  "text": "full tweet text",
  "hasImages": true/false,
  "hasThread": true/false,
  "engagement": {
    "likes": number or null,
    "retweets": number or null,
    "replies": number or null
  },
  "category": "resource" or "project-idea",
  "confidence": 0.85,
  "tags": ["tag1", "tag2", "tag3"],
  "summary": "one-sentence key insight",
  "title": "suggested note title (4-6 words)",
  "relevance": "why this matters (2-3 sentences)"
}

CATEGORIZATION RULES:
- "resource" = learning material, reference, industry insights, tutorials, interesting facts
- "project-idea" = something that could be built, explored, or implemented
- "confidence" = 0.0 to 1.0 score indicating how certain you are about the categorization
  - 1.0 = very clear (obvious learning resource or obvious project idea)
  - 0.5 = unclear (could be either, ambiguous content, or not relevant to user)
  - Use 0.8+ for clear categorizations
  - Use 0.5-0.7 for uncertain cases

CONTEXT: User is a software engineer working on:
- AI/LLM projects (Claude API, RAG chatbots, Chrome extensions)
- Knowledge management systems
- Web development

Tags should be technical topics, technologies, or themes (max 5 tags).`;

  const result = await aiClient.generateContent([
    prompt,
    {
      inlineData: {
        mimeType: 'image/png',
        data: base64Image
      }
    }
  ]);

  const response = await result.response;
  const text = response.text();

  // Parse JSON response (handle potential markdown code blocks)
  let jsonText = text.trim();
  if (jsonText.startsWith('```')) {
    jsonText = jsonText.replace(/```json?\n?/g, '').replace(/```\n?$/g, '');
  }

  return JSON.parse(jsonText);
}

/**
 * Generate markdown note from tweet data
 */
function generateNote(tweetData, screenshotPath) {
  const today = new Date().toISOString().split('T')[0];

  const frontmatter = `---
created: ${today}
source: twitter
author: ${tweetData.author}
author_name: ${tweetData.authorName}
date: ${tweetData.date || 'unknown'}
tags: ${JSON.stringify(tweetData.tags)}
category: ${tweetData.category}
confidence: ${tweetData.confidence}
screenshot: "[[${screenshotPath}]]"
---`;

  const content = `# ${tweetData.title}

**Author:** ${tweetData.authorName} (${tweetData.author})
**Date:** ${tweetData.date || 'Unknown'}
${tweetData.engagement.likes ? `**Engagement:** ${tweetData.engagement.likes} ❤️ · ${tweetData.engagement.retweets} 🔄 · ${tweetData.engagement.replies} 💬` : ''}

## Tweet Content

> ${tweetData.text}

${tweetData.hasImages ? '\n![[' + screenshotPath + ']]\n' : ''}

## Key Insights

${tweetData.summary}

## Relevance

${tweetData.relevance}

## Related Notes

-

---
**Captured from:** [[00 - Inbox/📥 Quick Capture|Quick Capture]]
**Screenshot:** [[${screenshotPath}]]`;

  return `${frontmatter}\n\n${content}`;
}

/**
 * Save note to appropriate directory
 */
function saveNote(tweetData, noteContent, screenshot) {
  // Determine target directory based on confidence
  let targetDir;
  if (tweetData.confidence < CONFIG.confidenceThreshold) {
    targetDir = CONFIG.unsureDir;
  } else {
    targetDir = tweetData.category === 'resource'
      ? CONFIG.resourcesDir
      : CONFIG.projectsDir;
  }

  const dirPath = path.join(CONFIG.vaultPath, targetDir);

  // Create directory if needed
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }

  // Generate filename from title (sanitize)
  const filename = tweetData.title
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
    .substring(0, 50) + '.md';

  const filePath = path.join(dirPath, filename);

  if (CONFIG.dryRun) {
    console.log(`  [DRY RUN] Would save to: ${path.join(targetDir, filename)}`);
    return { saved: false, path: null };
  }

  fs.writeFileSync(filePath, noteContent);
  console.log(`  ✓ Saved: ${path.join(targetDir, filename)}`);

  return { saved: true, path: filePath };
}

/**
 * Log processing results
 */
function logResult(tweetData, screenshot, notePath) {
  const logPath = path.join(CONFIG.vaultPath, CONFIG.logFile);
  const timestamp = new Date().toISOString();
  const date = timestamp.split('T')[0];

  let logContent = '';
  if (fs.existsSync(logPath)) {
    logContent = fs.readFileSync(logPath, 'utf-8');
  } else {
    logContent = `# Tweet Processing Log\n\nAutomated processing log for tweet screenshots.\n\n---\n\n`;
  }

  const entry = `## ${date} - ${tweetData.title}

- **Author:** ${tweetData.author}
- **Category:** ${tweetData.category}
- **Tags:** ${tweetData.tags.join(', ')}
- **Note:** [[${path.basename(notePath, '.md')}]]
- **Screenshot:** [[${screenshot.relativePath}]]
- **Processed:** ${timestamp}

`;

  // Prepend new entry after header
  const headerEnd = logContent.indexOf('---\n\n') + 5;
  logContent = logContent.slice(0, headerEnd) + entry + logContent.slice(headerEnd);

  if (!CONFIG.dryRun) {
    fs.writeFileSync(logPath, logContent);
  }
}

/**
 * Mark screenshot as processed
 */
function markAsProcessed(filename) {
  processedScreenshots[filename] = {
    processedAt: new Date().toISOString(),
    provider: CONFIG.aiProvider
  };

  if (!CONFIG.dryRun) {
    fs.writeFileSync(processedFile, JSON.stringify(processedScreenshots, null, 2));
  }
}

/**
 * Main processing function
 */
async function main() {
  console.log('🐦 Xeet Screenshot Processor');
  console.log('================================\n');
  console.log(`Vault: ${CONFIG.vaultPath}`);
  console.log(`AI Provider: ${CONFIG.aiProvider}`);
  console.log(`Confidence Threshold: ${CONFIG.confidenceThreshold} (xeets below this go to Inbox for review)`);
  console.log(`Mode: ${CONFIG.dryRun ? 'DRY RUN' : 'LIVE'}\n`);

  // Find new screenshots
  const screenshots = findNewScreenshots();

  if (screenshots.length === 0) {
    console.log('✓ No new screenshots to process');
    return;
  }

  console.log(`Found ${screenshots.length} new screenshot(s)\n`);

  let processed = 0;
  let failed = 0;

  // Process each screenshot
  for (const screenshot of screenshots) {
    try {
      console.log(`Processing: ${screenshot.filename}`);

      // Analyze with AI
      const tweetData = await analyzeScreenshot(screenshot.fullPath);
      console.log(`  Category: ${tweetData.category} (confidence: ${tweetData.confidence.toFixed(2)})`);
      if (tweetData.confidence < CONFIG.confidenceThreshold) {
        console.log(`  ⚠️  Low confidence - routing to: ${CONFIG.unsureDir}`);
      }
      console.log(`  Tags: ${tweetData.tags.join(', ')}`);

      // Generate note
      const noteContent = generateNote(tweetData, screenshot.relativePath);

      // Save note
      const result = saveNote(tweetData, noteContent, screenshot);

      if (result.saved || CONFIG.dryRun) {
        // Log result
        if (result.path) {
          logResult(tweetData, screenshot, result.path);
        }

        // Mark as processed
        markAsProcessed(screenshot.filename);
        processed++;
      }

      console.log('');

    } catch (error) {
      console.error(`  ✗ Error processing ${screenshot.filename}:`, error.message);
      failed++;
      console.log('');
    }
  }

  // Summary
  console.log('================================');
  console.log(`✓ Processed: ${processed}`);
  if (failed > 0) {
    console.log(`✗ Failed: ${failed}`);
  }
  console.log('================================\n');
}

// Run the processor
main().catch(console.error);
