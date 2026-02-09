#!/usr/bin/env node

/**
 * Content Sync Script
 * 
 * Ensures landing page (Next.js) and app (Angular) stay in sync with shared content.
 * Automatically copies product-content.ts to both projects.
 * 
 * Run this before building either project:
 * - npm run sync-content
 */

const fs = require('fs');
const path = require('path');

const SOURCE = path.join(__dirname, '../shared-content/product-content.ts');
const TARGETS = [
    path.join(__dirname, '../projects/landing/lib/product-content.ts'),
    path.join(__dirname, '../projects/frontend/src/app/shared/product-content.ts'),
];

console.log('🔄 Syncing product content...\n');

// Check source exists
if (!fs.existsSync(SOURCE)) {
    console.error('❌ Source file not found:', SOURCE);
    process.exit(1);
}

const content = fs.readFileSync(SOURCE, 'utf8');

// Copy to each target
let successCount = 0;
TARGETS.forEach((target) => {
    try {
        // Create directory if it doesn't exist
        const dir = path.dirname(target);
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
            console.log(`📁 Created directory: ${path.relative(process.cwd(), dir)}`);
        }

        fs.writeFileSync(target, content, 'utf8');
        console.log(`✅ Synced to: ${path.relative(process.cwd(), target)}`);
        successCount++;
    } catch (error) {
        console.error(`❌ Failed to sync to ${target}:`, error.message);
    }
});

console.log(`\n✨ Content sync complete! (${successCount}/${TARGETS.length} targets updated)`);
console.log('💡 Tip: Run this script before building to ensure consistency.\n');
