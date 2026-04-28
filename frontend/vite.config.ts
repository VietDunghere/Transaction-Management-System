import babel from '@rolldown/plugin-babel';
import react, { reactCompilerPreset } from '@vitejs/plugin-react';
import * as path from 'node:path';
import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vitest/config';
import tailwindcss from '@tailwindcss/vite';

const projectRoot = path.dirname(fileURLToPath(import.meta.url));

// https://vite.dev/config/
export default defineConfig({
    plugins: [react(), tailwindcss(), babel({ presets: [reactCompilerPreset()] })],
    resolve: {
        alias: {
            '~': path.resolve(projectRoot, 'src'),
        },
    },
    test: {
        environment: 'jsdom',
        setupFiles: ['./src/test/setup.tsx'],
        clearMocks: true,
        restoreMocks: true,
    },
});
