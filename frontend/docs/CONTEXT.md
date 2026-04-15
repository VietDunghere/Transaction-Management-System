# Huza Fraud - Engineering Context

## 1) Runtime Stack

- react: 19.2.4
- react-dom: 19.2.4
- @tanstack/react-router: 1.168.22
- @tanstack/react-query: 5.99.0
- @tanstack/react-query-devtools: 5.99.0
- axios: 1.15.0
- zod: 4.3.6
- react-hook-form: 7.72.1
- @hookform/resolvers: 5.2.2
- zustand: 5.0.12
- immer: 11.1.4
- tailwindcss: 4.2.2
- @tailwindcss/vite: 4.2.2
- clsx: 2.1.1
- normalize.css: 8.0.1

## 2) Dev Tooling

- vite: 8.0.4
- @vitejs/plugin-react: 6.0.1
- @rolldown/plugin-babel: 0.2.2
- @babel/core: 7.29.0
- babel-plugin-react-compiler: 1.0.0
- typescript: 6.0.2
- eslint: 9.39.4
- @eslint/js: 9.39.4
- typescript-eslint: 8.58.0
- eslint-plugin-react-hooks: 7.0.1
- eslint-plugin-react-refresh: 0.5.2

## 3) Scripts

- dev: vite
- build: tsc -b && vite build
- lint: eslint .
- gc: node scripts/gen.mjs
- preview: vite preview

## 4) Baseline Conventions

### 4.1 TypeScript and module system

- ESM project (`type: module`).
- `moduleResolution: bundler`.
- `jsx: react-jsx`.
- Strict anti-noise flags enabled:
    - `noUnusedLocals`
    - `noUnusedParameters`
    - `noFallthroughCasesInSwitch`

### 4.2 Import alias

- `~` maps to `src`.
- Prefer aliased imports for cross-folder references.

### 4.3 Architecture direction

- Feature-first for business domains.
- Keep clear boundaries:
    - layouts for app shell composition.
    - routes for route tree and router wiring.
    - api for transport and endpoint clients.
    - hooks for orchestration logic.
    - components for presentational units.

### 4.4 Routing pattern (TanStack Router)

- Use one root route as composition point.
- Render shared layout at root route level.
- Add public routes as root children.
- Keep route components small and focused.

### 4.5 API and data flow pattern

- Axios as transport client with a single entry point.
- React Query for server-state synchronization.
- Zod as validation boundary for external input.
- RHF + Zod resolver for forms.
- Zustand + Immer for local UI/domain state where React state is insufficient.

### 4.6 Styling pattern

- TailwindCSS v4 utility-first styling.
- `normalize.css` loaded globally.
- `clsx` for conditional class composition.

### 4.7 Barrel (barrier) pattern

- Each module folder should expose an `index.ts` or `index.tsx` as public surface.
- Consumers import from barrel path, avoid deep imports by default.

## 5) Current Routing Baseline

- Layout component: `src/layouts/DefaultLayout/DefaultLayout.tsx`.
- Public route sample target: `/test` with content `DEMO`.
- Root app entry stays in `src/main.tsx`, router provider mounted there.

## 6) Quality Rules for Ongoing Work

- Prefer immutable updates.
- Keep files focused and small.
- Avoid `any`; prefer explicit types or inferred types from schemas.
- Keep side effects and data fetching out of presentational components.
