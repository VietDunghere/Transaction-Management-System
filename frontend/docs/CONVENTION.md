# Convention for Huzafraud Frontend Development

This document outlines the architectural conventions and role definitions for the Huzafraud frontend. It serves as a guide for developers to maintain a clean separation of concerns, ensuring that each technology is used in its intended capacity. By adhering to these conventions, we can create a maintainable, scalable, and efficient frontend application.

## 1. Barrel Files
- **Purpose:** To centralize exports and simplify import statements across the codebase.
- **Convention:** Each directory (e.g., components like `Button`, `Modal`) should have an `index.tsx` file that re-exports all relevant modules. This allows for cleaner imports and better organization.

## 2. Naming 
- **Components:** Use PascalCase (e.g., `TransactionTable`, `UserProfile`).
- **Hooks:** Use camelCase with a `use` prefix (e.g., `useFetchTransactions`, `useAuth`).
- **Zustand Stores:** Use camelCase with a `use` prefix (e.g., `useGlobalStore`, `useAuthStore`).
- **Utility Functions:** Use camelCase (e.g., `formatDate`, `calculateRiskScore`).  

## 3. Technology Role Definitions (The Orchestration Layer)

- **React (The View Layer):** Responsible for the UI structure and local component state. Components should be "functional" and focused on rendering. Logic should be extracted into custom hooks to keep components lean.
- **TanStack Query (Server State):** The **exclusive** manager for all asynchronous data fetching, caching, and synchronization with the Python backend. Handles banking transactions, fraud logs, and user profiles.
- **Zustand (Client State):** The manager for global UI state that does not persist in the database. Use this for theme toggling, sidebar collapse states, and temporary session flags.
- **TanStack Router (The Type-Safe Skeleton):** Responsible for navigation, nested layouts, and URL-based state. It ensures that routes and search parameters (like transaction filters) are strictly typed using Zod schemas.
- **Tailwind CSS (Styling Engine):** The utility-first engine for all layouts. Follow the **Neo-Brutalist** aesthetic (high contrast, thick borders, Bento Box grids).
- **Shadcn UI (UI Primitives):** The source for accessible, pre-built components. Customize these using Tailwind to maintain design consistency across the fraud dashboard.

## 4. Routing & Navigation Guide

### 4.1 File-Based Routing
- **Structure:** All routes are defined in the `src/routes` directory. 
- **Convention:** - `__root.tsx`: The main layout shell (contains the Sidebar, Navbar, and `<Outlet />`).
    - `index.tsx`: The root dashboard view.
    - `transactions/index.tsx`: The transaction ledger.
    - `transactions.$id.tsx`: Dynamic route for specific fraud incident details.

### 4.2 Type-Safe Search Params
- **Requirement:** Every route that involves filtering (e.g., filtering transactions by risk level) must define a **Zod schema** for its search parameters.
- **Implementation:** Use `validateSearch` in the route definition. This prevents the application from entering an invalid state due to malformed URLs and provides auto-completion for search params.

### 4.3 Data Loading & Prefetching
- **Convention:** Use the Route `loader` function to trigger data fetching.
- **Integration:** The loader should call `queryClient.ensureQueryData` from TanStack Query. This ensures that data is already in the cache before the component renders, eliminating "loading flicker" and providing a "no-spinners" experience.

## 5. Directory Structure (MVVM-Inspired)

- `src/routes/`: File-based route definitions for TanStack Router.
- `src/components/`: Shadcn and custom shared UI components.
- `src/hooks/`: Custom TanStack Query hooks (e.g., `useTransactions.ts`).
- `src/stores/`: Zustand store definitions (e.g., `useUIStore.ts`).
- `src/services/`: API client instances and raw endpoint definitions.
- `src/utils/`: Helper functions for data formatting and anomaly detection math.

## 6. Implementation Rules

- **No Side Effects in Components:** Never use `useEffect` for data fetching. All backend data must be handled by TanStack Query.
- **Component Purity:** Keep components "dumb." If a component needs to calculate a complex risk score, move that logic to `src/utils/`.
- **Navigation:** Always use the `<Link>` component or `useNavigate` hook from TanStack Router to maintain type safety. Never use standard `<a>` tags for internal links.
- **Zustand Usage:** Only use Zustand if the state is truly global and not better handled by the URL (via TanStack Router) or the cache (via TanStack Query).

## 7. Performance & State Management Patterns

- **Query Keys as Dependency Arrays:** Treat TanStack Query keys like dependency arrays. Ensure that search parameters from TanStack Router are included in the query key to trigger automatic refetching when the URL changes.
- **Optimistic Updates:** For high-frequency actions (e.g., dismissing a false-positive fraud alert), implement optimistic updates via `onMutate` in TanStack Query. The UI should reflect the change immediately while the Python backend processes the request.
- **Selective Re-renders:** When using Zustand, always use "selectors" (e.g., `const isSidebarOpen = useUIStore(state => state.isSidebarOpen)`) to ensure components only re-render when the specific piece of state they consume changes.

## 8. Error & Loading Boundaries

- **Route-Level Error Components:** Define an `errorComponent` for each major route in TanStack Router. If a transaction fails to load or the ML service is down, the user should see a graceful, Neo-Brutalist styled error state rather than a blank screen.
- **Pending States:** Use the `pendingComponent` in TanStack Router to show a global progress bar or a specific Shadcn skeleton for the dashboard during the initial data load.
- **Toast Notifications:** Reserve Shadcn's `Toast` for **Mutation** results (e.g., "Transaction successfully blocked" or "Threshold updated"). Do not use toasts for initial data fetching.