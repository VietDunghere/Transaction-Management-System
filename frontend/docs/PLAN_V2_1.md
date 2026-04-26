# PLAN V2.1 — Fix Persisting Issues from TEST_RESULT (26/04/2026)

## Root Cause Analysis

### The Single Bug Behind 2 Symptoms

The **"undefined total"** and **"no pagination"** issues share one root cause: a **response shape mismatch** between backend and frontend.

| | Backend (actual) | Frontend (expected) |
|---|---|---|
| Shape | `{ data, pagination: { page, page_size, total_items, total_pages } }` | `{ total, page, limit, data }` |
| Total | `response.pagination.total_items` | `response.total` |
| Pages | `response.pagination.total_pages` | `Math.ceil(response.total / response.limit)` |

**Result:** `data.total` = `undefined` -> displays "undefined total". `NaN > 1` = `false` -> Pagination never renders.

---

## Fix 1: Pagination & Total Display (HIGH priority)

**Strategy:** Align frontend types to match backend response.

**`frontend/src/types/api.ts`** — Replace `PagedResponse<T>`:
```typescript
export interface PaginationMeta {
    page: number;
    page_size: number;
    total_items: number;
    total_pages: number;
}
export interface PagedResponse<T> {
    data: T[];
    pagination: PaginationMeta;
}
```

**5 list pages** — each needs 2 changes:
- Total display: `data.total` -> `data.pagination.total_items`
- Pagination: `Math.ceil(data.total / data.limit)` -> `data.pagination.total_pages`

| File |
|---|
| `pages/TransactionListPage/TransactionListPage.tsx` |
| `pages/LoanListPage/LoanListPage.tsx` |
| `pages/CaseListPage/CaseListPage.tsx` |
| `pages/UserListPage/UserListPage.tsx` |
| `pages/AuditLogListPage/AuditLogListPage.tsx` |

---

## Fix 2: Remove Email from Profile (LOW priority)

**File:** `frontend/src/pages/ProfilePage/ProfilePage.tsx` — delete the Email `KeyValueRow`.

---

## Fix 3: Dashboard Fraud Trend Chart (MEDIUM priority)

**Library:** Apache ECharts (`echarts` + `echarts-for-react`)

**File:** `frontend/src/pages/DashboardPage/DashboardPage.tsx`

**Available data** from `GET /dashboard/fraud-trend`:
`period_label`, `total_txn`, `approved`, `rejected`, `manual_review`, `fraud_rate` (daily, up to 90 days)

**Chart:** Zoomable Time-Series Area Chart
- X-axis: `period_label` (date)
- Series: `approved`, `rejected`, `manual_review` (stacked area)
- `dataZoom` slider for time-range scrubbing
- `toolbox` with save-as-image
- `tooltip` showing all series on hover

> Advanced charts (Fraud Ring Graph, Sankey, Seasonal Heatmap) evaluated but **skipped** — current API only exposes time-series aggregates, not per-transaction node/edge, channel-flow, or 365-day data.

---

## Fix 4: Model Performance Charts (MEDIUM priority)

**Library:** Recharts

**File:** `frontend/src/pages/AnalystModelPerformancePage/AnalystModelPerformancePage.tsx`

**Available data:**
- Fraud: `approved_count`, `review_count`, `rejected_count`, `false_positive_count/rate`
- Loan: `low/medium/high_risk_count`, `approved/rejected/pending_count`

**Charts:**
- **Fraud tab:** Donut chart — score distribution (approved / review / rejected)
- **Loan tab:** Stacked Bar chart — risk distribution + decision breakdown
- `ResponsiveContainer` for auto-sizing in existing layout

> Advanced charts (Scatter Jitter, Candlestick, Calendar Heatmap) evaluated but **skipped** — current API returns aggregate counts only, not per-transaction scores or hourly OHLC data.

---

## Execution Order

| Step | Fix | Deps |
|---|---|---|
| 1 | `pnpm add echarts echarts-for-react recharts` | — |
| 2 | Fix 1 — Pagination (6 files) | — |
| 3 | Fix 2 — Profile email (1 line) | — |
| 4 | Fix 3 — Dashboard ECharts zoomable chart | Step 1 |
| 5 | Fix 4 — Model Performance Recharts donuts + bars | Step 1 |

---

## Verification Checklist

- [ ] All list pages show correct total + working pagination
- [ ] Profile page has no Email field
- [ ] Dashboard fraud trend: zoomable time-series chart with dataZoom + toolbox
- [ ] Model Performance: donut chart (fraud) + stacked bar chart (loan) with ResponsiveContainer
