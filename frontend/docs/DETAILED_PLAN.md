# Detailed Implementation Plan: API-to-Page Mapping

> **Generated:** 2026-04-17
> **Branch:** frontend_biden
> **Status:** Approved, ready for implementation

---

## 1. Complete Route Tree

```
rootRoute (minimal shell, just <Outlet/>)
├── /login                          LoginPage (PublicLayout, no sidebar)
├── /loans/simulate                 LoanSimulatePage (public, no auth)
│
└── _auth (AuthLayout guard → DefaultLayout)
    ├── /                           DashboardPage
    ├── /profile                    ProfilePage (change password)
    ├── /transactions               TransactionListPage
    ├── /transactions/submit        TransactionSubmitPage
    ├── /transactions/$txnId        TransactionDetailPage
    ├── /cases                      CaseListPage
    ├── /cases/$caseId              CaseDetailPage
    ├── /users                      UserListPage
    ├── /users/create               UserCreatePage
    ├── /users/$userId              UserDetailPage
    ├── /loans                      LoanListPage
    ├── /loans/create               LoanCreatePage
    ├── /loans/$loanId              LoanDetailPage
    ├── /audit-logs                 AuditLogListPage
    ├── /audit-logs/$logId          AuditLogDetailPage
    ├── /reports                    ReportsPage
    ├── /etl                        EtlLogListPage
    ├── /ui-demo                    UIDemoPage (dev only)
    └── *                           NotFoundPage (404)
```

**Key change:** Split rootRoute into public layout (`/login`, `/loans/simulate`) and authenticated layout (`_auth` with `beforeLoad` guard + DefaultLayout).

---

## 2. API Endpoint → Page Mapping

### UC02 -- Auth (P0)

| Endpoint                    | Page/Location                              | Template          |
| --------------------------- | ------------------------------------------ | ----------------- |
| `POST /auth/login`          | `/login` LoginPage                         | Custom full-screen |
| `POST /auth/logout`         | Header user dropdown (action)              | N/A               |
| `GET /auth/me`              | Auth layout `beforeLoad` + Header display  | N/A               |
| `PATCH /auth/change-password` | `/profile` ProfilePage                   | FormPageTemplate  |
| `POST /auth/refresh`        | Axios 401 interceptor (transparent)        | N/A               |

### UC03 -- Transactions (P0)

| Endpoint                                   | Page/Route                                   | Template              |
| ------------------------------------------ | -------------------------------------------- | --------------------- |
| `GET /transactions`                        | `/transactions` TransactionListPage          | ListPageTemplate      |
| `GET /transactions/{txn_id}`               | `/transactions/$txnId` TransactionDetailPage | DetailPageTemplate    |
| `POST /transactions/submit`                | `/transactions/submit` TransactionSubmitPage | FormPageTemplate      |
| `GET /transactions/{txn_id}/state-history` | `/transactions/$txnId` (timeline section)    | DetailPageTemplate.timeline |

### UC05 -- Cases (P0)

| Endpoint                            | Page/Route                              | Template           |
| ----------------------------------- | --------------------------------------- | ------------------ |
| `GET /cases`                        | `/cases` CaseListPage                   | ListPageTemplate   |
| `GET /cases/{case_id}`              | `/cases/$caseId` CaseDetailPage         | DetailPageTemplate |
| `POST /cases/{case_id}/assign`      | `/cases/$caseId` (action button)        | In-page mutation   |
| `PATCH /cases/{case_id}/decision`   | `/cases/$caseId` (decision modal)       | Modal in DetailPage |

### UC08 -- Dashboard & Reports (P0)

| Endpoint                      | Page/Route                          | Template                   |
| ----------------------------- | ----------------------------------- | -------------------------- |
| `GET /dashboard/summary`      | `/` DashboardPage (KPI cards)       | DashboardTemplate          |
| `GET /dashboard/fraud-trend`  | `/` DashboardPage (chart section)   | DashboardTemplate.chartRow |
| `GET /reports/transactions`   | `/reports` ReportsPage (tab 1)      | ListPageTemplate           |
| `GET /reports/fraud`          | `/reports` ReportsPage (tab 2)      | ListPageTemplate           |

### UC04 -- Users (P1)

| Endpoint                            | Page/Route                            | Template           |
| ----------------------------------- | ------------------------------------- | ------------------ |
| `GET /users`                        | `/users` UserListPage                 | ListPageTemplate   |
| `POST /users`                       | `/users/create` UserCreatePage        | FormPageTemplate   |
| `GET /users/{user_id}`              | `/users/$userId` UserDetailPage       | DetailPageTemplate |
| `PATCH /users/{user_id}/disable`    | `/users/$userId` (action button)      | In-page mutation   |
| `PATCH /users/{user_id}/enable`     | `/users/$userId` (action button)      | In-page mutation   |
| `PATCH /users/{user_id}/role`       | `/users/$userId` (role select modal)  | Modal in DetailPage |

### UC06 -- Loans (P1)

| Endpoint                           | Page/Route                           | Template           |
| ---------------------------------- | ------------------------------------ | ------------------ |
| `POST /loans`                      | `/loans/create` LoanCreatePage       | FormPageTemplate   |
| `GET /loans`                       | `/loans` LoanListPage                | ListPageTemplate   |
| `GET /loans/{loan_id}`             | `/loans/$loanId` LoanDetailPage      | DetailPageTemplate |
| `POST /loans/simulate`             | `/loans/simulate` LoanSimulatePage   | FormPageTemplate (public) |
| `PATCH /loans/{loan_id}/decision`  | `/loans/$loanId` (decision modal)    | Modal in DetailPage |

### UC07 -- Audit Logs (P1)

| Endpoint                                          | Page/Route                             | Template              |
| ------------------------------------------------- | -------------------------------------- | --------------------- |
| `GET /audit-logs`                                 | `/audit-logs` AuditLogListPage         | ListPageTemplate      |
| `GET /audit-logs/entities/{entity_type}/{entity_id}` | Linked from detail pages            | ListPageTemplate filtered |
| `GET /audit-logs/{log_id}`                        | `/audit-logs/$logId` AuditLogDetailPage | DetailPageTemplate   |

### UC09 -- ETL Pipeline (P1)

| Endpoint          | Page/Route                        | Template         |
| ----------------- | --------------------------------- | ---------------- |
| `POST /etl/run`   | `/etl` (trigger button + form)    | In-page mutation |
| `GET /etl/logs`   | `/etl` EtlLogListPage             | ListPageTemplate |

---

## 3. Implementation Layers

### 3a. Types (`src/types/`)

- `src/types/api.ts` -- User, Role, Transaction, Case, Loan, AuditLog, EtlJob, PagedResponse<T>, ErrorResponse
- `src/types/searchParams.ts` -- Zod schemas for each list page filter params

### 3b. Services (`src/services/`)

| File                     | Methods                                                                    |
| ------------------------ | -------------------------------------------------------------------------- |
| `apiClient.ts`           | Shared Axios instance (base URL from env)                                  |
| `authService.ts`         | login, logout, getMe, changePassword, refreshToken                        |
| `transactionService.ts`  | getTransactions, getTransaction, submitTransaction, getTransactionStates   |
| `caseService.ts`         | getCases, getCase, assignCase, decideCase                                 |
| `userService.ts`         | getUsers, getUser, createUser, disableUser, enableUser, updateUserRole    |
| `loanService.ts`         | getLoans, getLoan, createLoan, simulateLoan, decideLoan                   |
| `auditService.ts`        | getAuditLogs, getAuditLog, getEntityAuditTrail                           |
| `dashboardService.ts`    | getSummary, getFraudTrend                                                  |
| `reportService.ts`       | getTransactionReport, getFraudReport, exportTransactionReport, exportFraudReport |
| `etlService.ts`          | triggerEtl, getEtlLogs                                                     |

### 3c. TanStack Query Hooks (`src/hooks/`)

| File                 | Queries                                                  | Mutations                                                     |
| -------------------- | -------------------------------------------------------- | ------------------------------------------------------------- |
| `useAuth.ts`         | useMe                                                    | useLogin, useLogout, useChangePassword                        |
| `useTransactions.ts` | useTransactions, useTransaction, useTransactionStates    | useSubmitTransaction                                          |
| `useCases.ts`        | useCases, useCase                                        | useAssignCase, useDecideCase                                  |
| `useUsers.ts`        | useUsers, useUser                                        | useCreateUser, useDisableUser, useEnableUser, useUpdateUserRole |
| `useLoans.ts`        | useLoans, useLoan                                        | useCreateLoan, useSimulateLoan, useDecideLoan                 |
| `useAuditLogs.ts`    | useAuditLogs, useAuditLog, useEntityAuditTrail           | --                                                            |
| `useDashboard.ts`    | useDashboardSummary, useFraudTrend                       | --                                                            |
| `useReports.ts`      | useTransactionReport, useFraudReport                     | useExportTransactionReport, useExportFraudReport              |
| `useEtl.ts`          | useEtlLogs                                               | useTriggerEtl                                                  |

### 3d. Stores (`src/stores/`)

| File               | State                                | Purpose                       |
| ------------------ | ------------------------------------ | ----------------------------- |
| `useAuthStore.ts`  | user, isAuthenticated, isLoading     | Auth state, RBAC source       |
| `useUIStore.ts`    | sidebarCollapsed, theme              | Global UI state               |

### 3e. Shared Infrastructure

| File                                      | Purpose                                                  |
| ----------------------------------------- | -------------------------------------------------------- |
| `src/lib/queryClient.ts`                  | QueryClient with defaults (staleTime, retry)             |
| `src/utils/localStorage.ts`               | Extend: setAccessToken, refresh token helpers, clearTokens |
| `src/utils/requireRole.ts`                | Route guard helper: throws redirect if role not allowed  |
| `src/layouts/PublicLayout/PublicLayout.tsx` | Minimal layout for /login (no sidebar)                  |

---

## 4. Auth Flow

1. **Login:** `POST /auth/login` → store tokens → setUser → redirect to `/`
2. **Session check:** Auth layout `beforeLoad` → getAccessToken → `GET /auth/me` → populate store (or redirect to `/login`)
3. **Token refresh:** Axios 401 interceptor → `POST /auth/refresh` → retry original request (mutex to prevent concurrent refreshes)
4. **Logout:** Header dropdown → `POST /auth/logout` → clearTokens → clearAuth → queryClient.clear() → redirect `/login`

---

## 5. RBAC Route Protection

| Route                 | OPERATOR        | REVIEWER | MANAGER     | ADMIN       |
| --------------------- | --------------- | -------- | ----------- | ----------- |
| `/` (Dashboard)       | → `/transactions` | → `/cases` | Full      | Full        |
| `/transactions`       | Yes (own)       | Read     | Read        | Read        |
| `/transactions/submit` | Yes            | --       | --          | --          |
| `/cases`              | --              | Full     | Read        | Read        |
| `/users`              | --              | --       | Read        | Full        |
| `/loans`              | Yes (own)       | --       | Read+Decide | Read+Decide |
| `/loans/simulate`     | Yes             | Yes      | Yes         | Yes         |
| `/audit-logs`         | --              | --       | Yes         | Yes         |
| `/reports`            | --              | --       | Yes         | Yes         |
| `/etl`                | --              | --       | --          | Yes         |
| `/profile`            | Yes             | Yes      | Yes         | Yes         |

Implementation: `beforeLoad` guard on each route calling `requireRole(allowedRoles, user.role)`. Sidebar filters nav items by role.

---

## 6. Execution Sequence

### Wave 0: Infrastructure (prerequisite for all features)

1. `src/lib/queryClient.ts` + wrap in `QueryClientProvider` in `main.tsx`
2. `src/services/apiClient.ts` (shared instance)
3. Enhance `src/api/callApi.ts` with refresh token interceptor
4. Extend `src/utils/localStorage.ts`
5. `src/stores/useAuthStore.ts` + `src/stores/useUIStore.ts`
6. `src/types/api.ts` + `src/types/searchParams.ts`
7. Restructure `src/routes/index.tsx` (public vs auth layout split)
8. `src/utils/requireRole.ts`
9. `src/layouts/PublicLayout/PublicLayout.tsx`

### Wave 1: P0 (UC02 + UC03 + UC05 + UC08)

1. Auth: service → hooks → LoginPage → ProfilePage → Header update
2. Transactions: service → hooks → ListPage → DetailPage → SubmitPage
3. Cases: service → hooks → ListPage → DetailPage (with assign + decision)
4. Dashboard: service → hooks → DashboardPage (replace PublicHomePage) → ReportsPage

### Wave 2: P1 (UC04 + UC06 + UC07 + UC09)

1. Users: service → hooks → ListPage → CreatePage → DetailPage
2. Loans: service → hooks → ListPage → CreatePage → DetailPage → SimulatePage
3. Audit: service → hooks → ListPage → DetailPage
4. ETL: service → hooks → EtlLogListPage

### Wave 3: Polish

1. Sidebar nav items filtered by role
2. Dynamic breadcrumbs in Header
3. 404/403 pages
4. Error boundaries (`errorComponent`) per route
5. Loading skeletons (`pendingComponent`) per route
6. Optimistic locking conflict UI (409 handling)
7. Export/download flow
8. Responsive QA

---

## 7. Pages Summary (20 new pages)

| #  | Page                   | Route                  | Template           | Wave |
| -- | ---------------------- | ---------------------- | ------------------ | ---- |
| 1  | LoginPage              | `/login`               | Custom             | W1   |
| 2  | DashboardPage          | `/`                    | DashboardTemplate  | W1   |
| 3  | ProfilePage            | `/profile`             | FormPageTemplate   | W1   |
| 4  | TransactionListPage    | `/transactions`        | ListPageTemplate   | W1   |
| 5  | TransactionDetailPage  | `/transactions/$txnId` | DetailPageTemplate | W1   |
| 6  | TransactionSubmitPage  | `/transactions/submit` | FormPageTemplate   | W1   |
| 7  | CaseListPage           | `/cases`               | ListPageTemplate   | W1   |
| 8  | CaseDetailPage         | `/cases/$caseId`       | DetailPageTemplate | W1   |
| 9  | ReportsPage            | `/reports`             | ListPageTemplate   | W1   |
| 10 | UserListPage           | `/users`               | ListPageTemplate   | W2   |
| 11 | UserCreatePage         | `/users/create`        | FormPageTemplate   | W2   |
| 12 | UserDetailPage         | `/users/$userId`       | DetailPageTemplate | W2   |
| 13 | LoanListPage           | `/loans`               | ListPageTemplate   | W2   |
| 14 | LoanCreatePage         | `/loans/create`        | FormPageTemplate   | W2   |
| 15 | LoanDetailPage         | `/loans/$loanId`       | DetailPageTemplate | W2   |
| 16 | LoanSimulatePage       | `/loans/simulate`      | FormPageTemplate   | W2   |
| 17 | AuditLogListPage       | `/audit-logs`          | ListPageTemplate   | W2   |
| 18 | AuditLogDetailPage     | `/audit-logs/$logId`   | DetailPageTemplate | W2   |
| 19 | EtlLogListPage         | `/etl`                 | ListPageTemplate   | W2   |
| 20 | NotFoundPage           | `*`                    | Custom             | W3   |

---

## 8. Files to Modify

| File                                           | Change                                                          |
| ---------------------------------------------- | --------------------------------------------------------------- |
| `src/routes/index.tsx`                         | Full restructure: public/auth split, 20+ routes, beforeLoad guards |
| `src/api/callApi.ts`                           | Add refresh token interceptor with mutex                        |
| `src/utils/localStorage.ts`                    | Add setAccessToken, refresh token helpers, clearTokens          |
| `src/layouts/DefaultLayout/Sidebar.tsx`        | Role-filtered navigation items, updated links                   |
| `src/layouts/DefaultLayout/Header.tsx`         | User info from auth store, logout dropdown, breadcrumbs         |
| `src/layouts/DefaultLayout/DefaultLayout.tsx`  | Move to auth layout child (no longer at root)                   |
| `src/main.tsx`                                 | Add QueryClientProvider + RouterProvider restructure            |
| `src/pages/index.ts`                           | Export all new pages                                            |

---

## 9. Verification

1. `npm run dev` -- app starts, `/login` shows login form
2. Login with test credentials → redirects to role-appropriate page
3. Navigate all routes → correct page renders with correct template
4. Check RBAC: OPERATOR cannot access `/users`, REVIEWER cannot access `/audit-logs`, etc.
5. List pages: filters work, pagination works, data loads from API
6. Detail pages: data loads, action buttons visible per role
7. Forms: validation works, submit calls correct endpoint, redirects on success
8. Logout: clears state, redirects to `/login`
9. Token expiry: 401 triggers refresh, transparent to user
