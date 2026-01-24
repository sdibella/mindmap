#!/usr/bin/env node

/**
 * Scan vault folder structure for Claude Code
 * Returns existing folders in Resources, Areas, and Projects
 */

const fs = require('fs');
const path = require('path');

const VAULT_PATH = process.env.VAULT_PATH || path.join(process.env.HOME, 'Library/Mobile Documents/iCloud~md~obsidian/Documents/StefanEternal');

function scanVaultFolders() {
  const folders = {
    resources: [],
    areas: [],
    projects: []
  };

  function scanDir(basePath, type) {
    const fullPath = path.join(VAULT_PATH, basePath);
    if (!fs.existsSync(fullPath)) return;

    const entries = fs.readdirSync(fullPath, { withFileTypes: true });
    for (const entry of entries) {
      if (entry.isDirectory() && !entry.name.startsWith('.')) {
        folders[type].push({
          name: entry.name,
          relativePath: path.join(basePath, entry.name),
          fullPath: path.join(fullPath, entry.name)
        });
      }
    }
  }

  scanDir('03 - Resources', 'resources');
  scanDir('02 - Areas', 'areas');
  scanDir('01 - Projects', 'projects');

  return folders;
}

// Run and output JSON
const folders = scanVaultFolders();
console.log(JSON.stringify(folders, null, 2));
