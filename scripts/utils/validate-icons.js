#!/usr/bin/env node

/**
 * Lucide Icon Validator
 * Scans Angular project for invalid Lucide icon names
 */

const fs = require('fs');
const path = require('path');

// Valid Lucide icons (common ones used in the project)
const VALID_ICONS = [
    'folder', 'sparkles', 'image', 'shield', 'settings',
    'chevron-down', 'chevron-right', 'chevron-up',
    'play', 'pause', 'download', 'share-2', 'x',
    'users', 'user', 'circle-user',
    'arrow-left', 'arrow-right',
    'external-link', 'trash-2', 'edit-2',
    'check', 'alert-circle', 'info'
];

// Icon name corrections
const ICON_CORRECTIONS = {
    'chevron-left': 'arrow-left',
    'user-round': 'circle-user',
    'users-round': 'users',
    'circle-user-round': 'circle-user',
    'circle-play': 'play',
    'play-circle': 'play'
};

function scanDirectory(dir, results = []) {
    const files = fs.readdirSync(dir);

    for (const file of files) {
        const filePath = path.join(dir, file);
        const stat = fs.statSync(filePath);

        if (stat.isDirectory() && !file.startsWith('.') && file !== 'node_modules') {
            scanDirectory(filePath, results);
        } else if (file.endsWith('.html') || file.endsWith('.ts')) {
            const content = fs.readFileSync(filePath, 'utf8');
            const iconMatches = content.matchAll(/name="([^"]+)"/g);

            for (const match of iconMatches) {
                const iconName = match[1];
                if (!VALID_ICONS.includes(iconName)) {
                    results.push({
                        file: filePath,
                        icon: iconName,
                        suggestion: ICON_CORRECTIONS[iconName] || 'unknown'
                    });
                }
            }
        }
    }

    return results;
}

const projectRoot = path.join(__dirname, 'projects/frontend/src/app');
const invalidIcons = scanDirectory(projectRoot);

if (invalidIcons.length > 0) {
    console.log('❌ Invalid Lucide icons found:\n');
    invalidIcons.forEach(({ file, icon, suggestion }) => {
        console.log(`  ${path.relative(process.cwd(), file)}`);
        console.log(`    Icon: "${icon}" → Suggested: "${suggestion}"\n`);
    });
    process.exit(1);
} else {
    console.log('✅ All Lucide icons are valid!');
    process.exit(0);
}
