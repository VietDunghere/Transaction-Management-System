const fs = require('fs');
const path = require('path');

const replacements = {
  // Spacing
  '\\[var\\(--spacing-xs\\)\\]': '1',
  '\\[var\\(--spacing-sm\\)\\]': '2',
  '\\[var\\(--spacing-md\\)\\]': '3',
  '\\[var\\(--spacing-base\\)\\]': '4',
  '\\[var\\(--spacing-lg\\)\\]': '6',
  '\\[var\\(--spacing-xl\\)\\]': '8',
  '\\[var\\(--spacing-2xl\\)\\]': '12',
  '\\[var\\(--spacing-3xl\\)\\]': '16',

  // Border Widths
  '\\[var\\(--border-width-base\\)\\]': '2',

  // Radii
  '\\[var\\(--radius-sm\\)\\]': 'sm',
  '\\[var\\(--radius-base\\)\\]': 'md',

  // Font Sizes
  '\\[var\\(--font-size-caption\\)\\]': 'sm',
  '\\[var\\(--font-size-small\\)\\]': 'xs',
  '\\[var\\(--font-size-body\\)\\]': 'base',
  '\\[var\\(--font-size-h3\\)\\]': 'xl',
  '\\[var\\(--font-size-h2\\)\\]': '2xl',
  '\\[var\\(--font-size-h1\\)\\]': '3xl',

  // Font Weights
  'font-\\[var\\(--font-weight-medium\\)\\]': 'font-medium',
  'font-\\[var\\(--font-weight-semibold\\)\\]': 'font-semibold',
  'font-\\[var\\(--font-weight-bold\\)\\]': 'font-bold',
  'font-\\[var\\(--font-weight-black\\)\\]': 'font-black',

  // Line Heights
  'leading-\\[var\\(--line-height-tight\\)\\]': 'leading-tight',

  // Colors
  '\\[var\\(--color-text-muted\\)\\]': '[#a3a3a3]',
  '\\[var\\(--color-text-secondary\\)\\]': '[#525252]',
  '\\[var\\(--color-text-primary\\)\\]': '[#1a1a1a]',
  '\\[var\\(--color-surface-secondary\\)\\]': '[#f5f5f0]',
  '\\[var\\(--color-surface-dark\\)\\]': '[#1a1a1a]',
  '\\[var\\(--color-surface\\)\\]': 'white',
  '\\[var\\(--color-border\\)\\]': '[#1a1a1a]',
  '\\[var\\(--color-border-light\\)\\]': '[#d4d4d4]',
  '\\[var\\(--color-accent-red\\)\\]': '[#ef4444]',

  // Transitions
  'duration-\\[var\\(--transition-fast\\)\\]': 'duration-150',
  'duration-\\[var\\(--transition-base\\)\\]': 'duration-300',
};

function processDirectory(dir) {
  const files = fs.readdirSync(dir);
  for (const file of files) {
    const fullPath = path.join(dir, file);
    const stat = fs.statSync(fullPath);
    if (stat.isDirectory()) {
      processDirectory(fullPath);
    } else if (fullPath.endsWith('.tsx') || fullPath.endsWith('.ts')) {
      let content = fs.readFileSync(fullPath, 'utf8');
      let changed = false;
      for (const [regexStr, replacement] of Object.entries(replacements)) {
        const regex = new RegExp(regexStr, 'g');
        if (regex.test(content)) {
          content = content.replace(regex, replacement);
          changed = true;
        }
      }
      if (changed) {
        fs.writeFileSync(fullPath, content, 'utf8');
        console.log(`Updated: ${fullPath}`);
      }
    }
  }
}

processDirectory('./src');
console.log('Done!');
