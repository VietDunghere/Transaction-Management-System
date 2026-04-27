# Demo Runner — Implementation Tracker

**Feature**: Integrate `demo_transactions.py` into backend as REST API + frontend page
**Started**: 2026-04-27
**Approach**: REST API (start/stop/status) with 1s frontend polling

---

## Architecture

```
[Frontend DemoPage]  ──1s poll──>  GET  /api/v1/demo/status
                     ──click───>  POST /api/v1/demo/start
                     ──click───>  POST /api/v1/demo/stop
                                       │
[DemoRunnerService]  ── singleton, runs asyncio.Task in background ──
     ├── calls TransactionService.submit() directly (no HTTP)
     ├── calls LoanService.apply() directly (no HTTP)
     ├── accumulates stats + last 50 events in memory
     └── one global instance — only 1 demo at a time
```

**Constraints**:
- Single demo instance globally (not per-user)
- Only OPERATOR role can start/stop/view
- Max rate: 10 req/s
- No new DB tables — reuses existing transactions_live, loans
- Ring buffer of 50 recent events in memory

---

## Checkpoints

### Backend

| # | File | Action | Status |
|---|------|--------|--------|
| B1 | `backend/app/schemas/demo.py` | CREATE — DemoStartRequest, DemoStatusResponse, DemoEvent | [x] |
| B2 | `backend/app/services/demo_runner_service.py` | CREATE — singleton service with asyncio.Task loop | [x] |
| B3 | `backend/app/api/v1/routes/demo.py` | CREATE — 3 endpoints (start/stop/status) | [x] |
| B4 | `backend/app/api/v1/router.py` | EDIT — register demo router | [x] |

### Frontend

| # | File | Action | Status |
|---|------|--------|--------|
| F1 | `frontend/src/services/demoService.ts` | CREATE — API calls | [x] |
| F2 | `frontend/src/pages/DemoPage/DemoPage.tsx` | CREATE — full page with config, stats, event log | [x] |
| F3 | `frontend/src/pages/DemoPage/index.ts` | CREATE — barrel export | [x] |
| F4 | `frontend/src/pages/index.ts` | EDIT — add DemoPage export | [x] |
| F5 | `frontend/src/routes/index.tsx` | EDIT — add /demo route (OPERATOR) | [x] |
| F6 | `frontend/src/layouts/DefaultLayout/Sidebar.tsx` | EDIT — add Demo Runner nav item | [x] |

### Cross-role Polling (when demo is running, list pages auto-refresh at 1s)

| # | File | Action | Status |
|---|------|--------|--------|
| P1 | `frontend/src/hooks/useDemoRunning.ts` | CREATE — shared hook, polls /demo/status every 5s | [x] |
| P2 | `frontend/src/hooks/useTransactions.ts` | EDIT — accept refetchInterval param | [x] |
| P3 | `frontend/src/hooks/useLoans.ts` | EDIT — accept refetchInterval param | [x] |
| P4 | `frontend/src/hooks/useCases.ts` | EDIT — accept refetchInterval param | [x] |
| P5 | `frontend/src/pages/TransactionListPage` | EDIT — 1s polling when demo running (ANALYST, MANAGER) | [x] |
| P6 | `frontend/src/pages/LoanListPage` | EDIT — 1s polling when demo running (OPERATOR, REVIEWER) | [x] |
| P7 | `frontend/src/pages/CaseListPage` | EDIT — 1s polling when demo running (REVIEWER) | [x] |
| P8 | `backend/app/api/v1/routes/demo.py` | GET /status open to all roles | [x] |

### Verification

| # | Check | Status |
|---|-------|--------|
| V1 | Backend starts without errors | [x] |
| V2 | Frontend compiles without errors | [x] |
| V3 | POST /demo/start returns 200, demo runs | [ ] |
| V4 | GET /demo/status returns stats + events | [ ] |
| V5 | POST /demo/stop cleanly stops demo | [ ] |
| V6 | Second start while running returns 409 | [ ] |

---

## Key Design Decisions

1. **Service calls, not HTTP**: DemoRunnerService imports TransactionService/LoanService and calls them directly with a fresh `SessionLocal()` per iteration — avoids self-HTTP overhead and auth token management.

2. **asyncio.Task**: FastAPI runs on uvicorn's asyncio loop. The demo loop is an async task that `await asyncio.sleep(delay)` between iterations. DB calls are sync (SQLAlchemy), wrapped in `asyncio.to_thread()` to avoid blocking the event loop.

3. **Ring buffer**: `collections.deque(maxlen=50)` stores recent events. Status endpoint serializes the deque snapshot — no DB query needed for polling.

4. **Graceful stop**: `asyncio.Task.cancel()` raises `CancelledError` inside the sleep, which the loop catches to exit cleanly.

5. **Faker not needed server-side**: The original script uses Faker for credit card numbers and IPs. We replicate this with Python's `random` + simple generators to avoid adding a dependency. Actually, we keep `faker` since it's already in requirements for the seed script — lightweight and gives realistic data.
