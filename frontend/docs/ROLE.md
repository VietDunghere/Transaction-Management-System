## Huzafraud Frontend Orchestration Role-Map

### 1. React + TSX (The UI Core / View Layer)
* **Role:** The Component Engine.
* **Responsibility:** Manages component lifecycle, local UI state (e.g., `isDropdownOpen`), and rendering logic.
* **Instruction for AI:** "Use functional components with hooks. Keep components small and focused on the View. Do not put complex business logic or fetch calls inside components."

### 2. TanStack Query (The Server State / Repository Layer)
* **Role:** The Data Synchronizer.
* **Responsibility:** All asynchronous communication with the backend (Python API). Handles caching, re-fetching banking transactions, and managing "Loading/Error" states.
* **Instruction for AI:** "All API calls must be wrapped in custom hooks using `useQuery` or `useMutation`. Treat this as the single source of truth for all database-derived data."

### 3. Zustand (The Client State / ViewModel Layer)
* **Role:** The Global Store.
* **Responsibility:** Manages data that *doesn't* live in a database but needs to be accessed everywhere. 
* **Instruction for AI:** "Use Zustand for global UI settings like 'Risk Threshold filters,' 'Auth Tokens,' and 'Sidebar state.' Keep the store minimal; if the data comes from an API, use TanStack Query instead."

### 4. Tailwind CSS (The Styling Engine)
* **Role:** The Design Language.
* **Responsibility:** Low-level styling and layout.
* **Instruction for AI:** "Use utility classes for all custom layouts. Maintain a strict color palette (e.g., your preferred Black & White/Neo-Brutalist style). Use the `cn()` utility for conditional classes."

### 5. Shadcn UI (The Component Library)
* **Role:** The UI Building Blocks.
* **Responsibility:** Providing accessible, high-quality primitives (Modals, Tables, Buttons, Cards).
* **Instruction for AI:** "Use Shadcn components as the base for the UI. Customize their styles via Tailwind to fit the Bento Box/Editorial aesthetic. Prioritize the Data Table component for transaction logs."
