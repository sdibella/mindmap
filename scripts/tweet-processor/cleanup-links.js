#!/usr/bin/env node

/**
 * One-time cleanup:
 * - Delete Readwise/Tweets files
 * - Remove x.com links from other files
 * - Delete files that become empty
 */

const fs = require('fs');
const path = require('path');
const data = require('./fetched-tweets.json');

const vaultPath = process.env.VAULT_PATH || path.join(process.env.HOME, 'Library/Mobile Documents/iCloud~md~obsidian/Documents/StefanEternal');

// Get all unique files
const files = new Set();
data.forEach(t => t.foundIn.forEach(f => files.add(f)));

const dryRun = process.argv.includes('--dry-run');

console.log(dryRun ? '🔍 DRY RUN - Preview mode\n' : '🧹 CLEANUP MODE - Will modify/delete files\n');

let linksRemoved = 0;
let filesModified = 0;
let filesDeleted = 0;

// Phase 1: Delete Readwise/Tweets files entirely
console.log('=== Phase 1: Delete Readwise/Tweets files ===\n');
Array.from(files).filter(f => f.startsWith('Readwise/Tweets/')).forEach(file => {
  const filePath = path.join(vaultPath, file);
  if (fs.existsSync(filePath)) {
    if (dryRun) {
      console.log(`[DRY RUN] Would delete: ${file}`);
    } else {
      fs.unlinkSync(filePath);
      console.log(`✓ Deleted: ${file}`);
      filesDeleted++;
    }
  }
});

// Phase 2: Remove links from other files
console.log('\n=== Phase 2: Remove x.com links from remaining files ===\n');
Array.from(files).filter(f => !f.startsWith('Readwise/Tweets/')).sort().forEach((file, i) => {
  const filePath = path.join(vaultPath, file);

  if (!fs.existsSync(filePath)) {
    return;
  }

  const content = fs.readFileSync(filePath, 'utf-8');
  const urlRegex = /https?:\/\/(x\.com|twitter\.com)\/[^\s\)]+/g;
  const matches = content.match(urlRegex);

  if (!matches || matches.length === 0) {
    return;
  }

  console.log(`${i+1}. ${file}`);
  console.log(`   Found ${matches.length} link(s)`);

  // Remove the links (just delete them, don't replace with text)
  const newContent = content.replace(urlRegex, '');

  // Check if file would be essentially empty after removal
  const contentWithoutFrontmatter = newContent.replace(/^---\n[\s\S]*?\n---\n/m, '').trim();
  const isEmpty = contentWithoutFrontmatter.length === 0 ||
                  contentWithoutFrontmatter.match(/^[\s\n]*$/);

  if (isEmpty) {
    if (dryRun) {
      console.log(`   [DRY RUN] Would DELETE (file becomes empty)`);
    } else {
      fs.unlinkSync(filePath);
      console.log(`   ✓ DELETED (file was empty after removal)`);
      filesDeleted++;
    }
  } else {
    if (dryRun) {
      console.log(`   [DRY RUN] Would remove ${matches.length} link(s)`);
    } else {
      fs.writeFileSync(filePath, newContent);
      console.log(`   ✓ Removed ${matches.length} link(s)`);
      filesModified++;
    }
  }

  linksRemoved += matches.length;
});

console.log('\n================================');
console.log(`Links removed: ${linksRemoved}`);
console.log(`Files modified: ${filesModified}`);
console.log(`Files deleted: ${filesDeleted}`);
if (dryRun) {
  console.log('\n💡 Run without --dry-run to execute cleanup');
} else {
  console.log('\n✅ Cleanup complete!');
}
console.log('================================\n');
