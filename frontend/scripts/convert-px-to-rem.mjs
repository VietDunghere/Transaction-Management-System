import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const srcRoot = path.resolve(scriptDir, '..', 'src');
const targetExtensions = new Set(['.ts', '.tsx', '.js', '.jsx']);

// Spacing-based utilities that support bare numeric values in Tailwind v4
// e.g. w-45, h-50, left-6, min-w-45, gap-7, p-6, m-4, size-25
const spacingPrefixes = new Set([
    'w', 'h', 'size',
    'min-w', 'max-w', 'min-h', 'max-h',
    'p', 'px', 'py', 'pt', 'pr', 'pb', 'pl', 'ps', 'pe',
    'm', 'mx', 'my', 'mt', 'mr', 'mb', 'ml', 'ms', 'me',
    'gap', 'gap-x', 'gap-y',
    'top', 'right', 'bottom', 'left',
    'inset', 'inset-x', 'inset-y',
    'start', 'end',
    'space-x', 'space-y',
    'indent',
    'translate-x', 'translate-y',
    'scroll-m', 'scroll-mx', 'scroll-my', 'scroll-mt', 'scroll-mr', 'scroll-mb', 'scroll-ml',
    'scroll-p', 'scroll-px', 'scroll-py', 'scroll-pt', 'scroll-pr', 'scroll-pb', 'scroll-pl',
    'basis',
]);

// Match both [Npx] and [Nrem] arbitrary values
const arbitraryPattern = /([a-zA-Z][a-zA-Z0-9-]*)-\[(\d+(?:\.\d+)?)(px|rem)\]/g;

/**
 * Convert a value to Tailwind spacing units (--spacing = 0.25rem = 4px)
 * and round to nearest 0.5
 */
function toSpacingUnits(value, unit) {
    let px;
    if (unit === 'px') {
        px = value;
    } else {
        // rem → px (base 16)
        px = value * 16;
    }
    // spacing units = px / 4
    const units = px / 4;
    // Round to nearest 0.5
    const rounded = Math.round(units * 2) / 2;
    // Format: no trailing .0
    return rounded % 1 === 0 ? String(rounded) : rounded.toFixed(1);
}

function walk(dir, files = []) {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
        const fullPath = path.join(dir, entry.name);

        if (entry.isDirectory()) {
            walk(fullPath, files);
            continue;
        }

        if (!targetExtensions.has(path.extname(entry.name))) {
            continue;
        }

        files.push(fullPath);
    }

    return files;
}

function run() {
    const files = walk(srcRoot);
    const changedFiles = [];
    let replacementCount = 0;

    for (const filePath of files) {
        const current = fs.readFileSync(filePath, 'utf8');

        const next = current.replace(arbitraryPattern, (match, utility, numStr, unit) => {
            const value = parseFloat(numStr);

            // Skip sub-pixel values (< 1px or < 0.0625rem)
            const px = unit === 'px' ? value : value * 16;
            if (px < 1) {
                return match;
            }

            // Only convert spacing-based utilities to bare format
            if (!spacingPrefixes.has(utility)) {
                return match;
            }

            replacementCount += 1;
            const spacingValue = toSpacingUnits(value, unit);
            return `${utility}-${spacingValue}`;
        });

        if (next === current) {
            continue;
        }

        fs.writeFileSync(filePath, next, 'utf8');
        changedFiles.push(path.relative(path.resolve(scriptDir, '..'), filePath));
    }

    console.log(`Replaced ${replacementCount} occurrence(s) across ${changedFiles.length} file(s).`);

    if (changedFiles.length > 0) {
        console.log('Changed files:');
        for (const file of changedFiles) {
            console.log(`- ${file}`);
        }
    }
}

run();
