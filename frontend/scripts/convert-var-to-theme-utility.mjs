import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const srcRoot = path.resolve(scriptDir, '..', 'src');
const targetExtensions = new Set(['.ts', '.tsx', '.js', '.jsx', '.css']);

// Match ANY utility-[var(--color-*)] pattern (text, border, ring, border-t, border-r, etc.)
const varPattern = /([a-zA-Z][a-zA-Z0-9-]*)-\[var\(--color-([a-z0-9-]+)\)\]/g;

function toUtility(prefix, token) {
    return `${prefix}-${token}`;
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

        const next = current.replace(varPattern, (_, prefix, token) => {
            replacementCount += 1;
            return toUtility(prefix, token);
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
