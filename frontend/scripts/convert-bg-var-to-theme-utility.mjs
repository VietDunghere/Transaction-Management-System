import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const srcRoot = path.resolve(scriptDir, '..', 'src');
const targetExtensions = new Set(['.ts', '.tsx', '.js', '.jsx', '.css']);
const bgVarPattern = /bg-\[var\(--color-([a-z0-9-]+)\)\]/g;

function toBgUtility(token) {
    const normalized = token.startsWith('bg-') ? token.slice(3) : token;
    return `bg-${normalized}`;
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

        const next = current.replace(bgVarPattern, (_, token) => {
            replacementCount += 1;
            return toBgUtility(token);
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
