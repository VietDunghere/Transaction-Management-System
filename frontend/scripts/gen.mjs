import fs from 'fs';
import path from 'path';

const componentName = process.argv[2];

if (!componentName) {
    console.error('Nhap ten Component di ma huhuhu!');
    process.exit(1);
}

const baseDir = path.join(process.cwd(), 'src', 'components', componentName);

fs.mkdirSync(baseDir, { recursive: true });

const componentCode = `export function ${componentName}() {
    return (
        <div>
            ${componentName} Component
        </div>
    );
};
`;

const indexCode = `export { default } from './${componentName}';`;

// 4. Ghi file
fs.writeFileSync(path.join(baseDir, `${componentName}.tsx`), componentCode);
fs.writeFileSync(path.join(baseDir, 'index.tsx'), indexCode);

console.log(`Created ${componentName} at src/components/`);
