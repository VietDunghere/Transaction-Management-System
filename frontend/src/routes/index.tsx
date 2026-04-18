import { Outlet, createRootRoute, createRoute, createRouter, redirect } from '@tanstack/react-router';
import { DefaultLayout } from '~/layouts/DefaultLayout';
import { PublicLayout } from '~/layouts/PublicLayout';
import {
    UIDemoPage,
    LoginPage,
    ProfilePage,
    DashboardPage,
    TransactionListPage,
    TransactionDetailPage,
    TransactionSubmitPage,
    CaseListPage,
    CaseDetailPage,
    ReportsPage,
    UserListPage,
    UserCreatePage,
    UserDetailPage,
    LoanListPage,
    LoanCreatePage,
    LoanDetailPage,
    LoanSimulatePage,
    AuditLogListPage,
    AuditLogDetailPage,
    EtlLogListPage,
    ForbiddenPage,
    NotFoundPage,
} from '~/pages';
import { useAuthStore } from '~/stores/useAuthStore';
import { getAccessToken } from '~/utils/localStorage';
import { LoadingSkeleton } from '~/components/ui/LoadingSkeleton/LoadingSkeleton';
import { ErrorState } from '~/components/ui/ErrorState/ErrorState';
import type { Role } from '~/types/api';

// ---- Helper: get role from store (for beforeLoad) ----

function getUserRole(): Role | undefined {
    return useAuthStore.getState().user?.role;
}

function guardRole(allowed: Role[]) {
    const role = getUserRole();
    if (role && !allowed.includes(role)) {
        throw redirect({ to: '/forbidden' });
    }
    // If role is undefined (store not loaded yet), let the page load —
    // the useMe query in pages will handle it
}

// ---- Root: minimal shell ----

const rootRoute = createRootRoute({
    component: () => <Outlet />,
});

// ============================================================
// PUBLIC ROUTES (no auth required)
// ============================================================

const publicLayoutRoute = createRoute({
    getParentRoute: () => rootRoute,
    id: 'public',
    component: PublicLayout,
});

const loginRoute = createRoute({
    getParentRoute: () => publicLayoutRoute,
    path: '/login',
    component: LoginPage,
});

const loanSimulateRoute = createRoute({
    getParentRoute: () => publicLayoutRoute,
    path: '/loans/simulate',
    component: LoanSimulatePage,
});

// ============================================================
// AUTHENTICATED ROUTES (require login -> DefaultLayout)
// ============================================================

const authLayoutRoute = createRoute({
    getParentRoute: () => rootRoute,
    id: 'auth',
    component: () => (
        <DefaultLayout>
            <Outlet />
        </DefaultLayout>
    ),
    beforeLoad: () => {
        const token = getAccessToken();
        if (!token) {
            throw redirect({ to: '/login' });
        }
    },
    pendingComponent: () => <LoadingSkeleton variant="card" />,
    errorComponent: ({ error }) => (
        <DefaultLayout>
            <ErrorState
                title="Something went wrong"
                description={error instanceof Error ? error.message : 'An unexpected error occurred.'}
                onRetry={() => window.location.reload()}
            />
        </DefaultLayout>
    ),
});

// -- Dashboard (MANAGER, ADMIN — others redirect to their primary page) --
const dashboardRoute = createRoute({
    getParentRoute: () => authLayoutRoute,
    path: '/',
    component: DashboardPage,
    beforeLoad: () => {
        const role = getUserRole();
        if (role === 'OPERATOR') {
            throw redirect({ to: '/transactions' });
        }
        if (role === 'REVIEWER') {
            throw redirect({ to: '/cases' });
        }
    },
});

// -- Profile (all authenticated) --
const profileRoute = createRoute({
    getParentRoute: () => authLayoutRoute,
    path: '/profile',
    component: ProfilePage,
});

// -- Forbidden --
const forbiddenRoute = createRoute({
    getParentRoute: () => authLayoutRoute,
    path: '/forbidden',
    component: ForbiddenPage,
});

// -- Transactions (all authenticated can view) --
const transactionsRoute = createRoute({
    getParentRoute: () => authLayoutRoute,
    path: '/transactions',
    component: TransactionListPage,
});

// -- Transaction Submit (OPERATOR only) --
const transactionSubmitRoute = createRoute({
    getParentRoute: () => authLayoutRoute,
    path: '/transactions/submit',
    component: TransactionSubmitPage,
    beforeLoad: () => guardRole(['OPERATOR']),
});

const transactionDetailRoute = createRoute({
    getParentRoute: () => authLayoutRoute,
    path: '/transactions/$txnId',
    component: TransactionDetailPage,
});

// -- Cases (REVIEWER, MANAGER, ADMIN) --
const casesRoute = createRoute({
    getParentRoute: () => authLayoutRoute,
    path: '/cases',
    component: CaseListPage,
    beforeLoad: () => guardRole(['REVIEWER', 'MANAGER', 'ADMIN']),
});

const caseDetailRoute = createRoute({
    getParentRoute: () => authLayoutRoute,
    path: '/cases/$caseId',
    component: CaseDetailPage,
    beforeLoad: () => guardRole(['REVIEWER', 'MANAGER', 'ADMIN']),
});

// -- Users (MANAGER, ADMIN) --
const usersRoute = createRoute({
    getParentRoute: () => authLayoutRoute,
    path: '/users',
    component: UserListPage,
    beforeLoad: () => guardRole(['MANAGER', 'ADMIN']),
});

const userCreateRoute = createRoute({
    getParentRoute: () => authLayoutRoute,
    path: '/users/create',
    component: UserCreatePage,
    beforeLoad: () => guardRole(['ADMIN']),
});

const userDetailRoute = createRoute({
    getParentRoute: () => authLayoutRoute,
    path: '/users/$userId',
    component: UserDetailPage,
    beforeLoad: () => guardRole(['MANAGER', 'ADMIN']),
});

// -- Loans (OPERATOR, MANAGER, ADMIN) --
const loansRoute = createRoute({
    getParentRoute: () => authLayoutRoute,
    path: '/loans',
    component: LoanListPage,
    beforeLoad: () => guardRole(['OPERATOR', 'MANAGER', 'ADMIN']),
});

const loanCreateRoute = createRoute({
    getParentRoute: () => authLayoutRoute,
    path: '/loans/create',
    component: LoanCreatePage,
    beforeLoad: () => guardRole(['OPERATOR', 'MANAGER', 'ADMIN']),
});

const loanDetailRoute = createRoute({
    getParentRoute: () => authLayoutRoute,
    path: '/loans/$loanId',
    component: LoanDetailPage,
    beforeLoad: () => guardRole(['OPERATOR', 'MANAGER', 'ADMIN']),
});

// -- Audit Logs (MANAGER, ADMIN) --
const auditLogsRoute = createRoute({
    getParentRoute: () => authLayoutRoute,
    path: '/audit-logs',
    component: AuditLogListPage,
    beforeLoad: () => guardRole(['MANAGER', 'ADMIN']),
});

const auditLogDetailRoute = createRoute({
    getParentRoute: () => authLayoutRoute,
    path: '/audit-logs/$logId',
    component: AuditLogDetailPage,
    beforeLoad: () => guardRole(['MANAGER', 'ADMIN']),
});

// -- Reports (MANAGER, ADMIN) --
const reportsRoute = createRoute({
    getParentRoute: () => authLayoutRoute,
    path: '/reports',
    component: ReportsPage,
    beforeLoad: () => guardRole(['MANAGER', 'ADMIN']),
});

// -- ETL (ADMIN only) --
const etlRoute = createRoute({
    getParentRoute: () => authLayoutRoute,
    path: '/etl',
    component: EtlLogListPage,
    beforeLoad: () => guardRole(['ADMIN']),
});

// -- UI Demo (dev only) --
const uiDemoRoute = createRoute({
    getParentRoute: () => authLayoutRoute,
    path: '/ui-demo',
    component: UIDemoPage,
});

// -- 404 --
const notFoundRoute = createRoute({
    getParentRoute: () => authLayoutRoute,
    path: '*',
    component: NotFoundPage,
});

// ============================================================
// ROUTE TREE
// ============================================================

const routeTree = rootRoute.addChildren([
    publicLayoutRoute.addChildren([loginRoute, loanSimulateRoute]),
    authLayoutRoute.addChildren([
        dashboardRoute,
        profileRoute,
        forbiddenRoute,
        transactionsRoute,
        transactionSubmitRoute,
        transactionDetailRoute,
        casesRoute,
        caseDetailRoute,
        usersRoute,
        userCreateRoute,
        userDetailRoute,
        loansRoute,
        loanCreateRoute,
        loanDetailRoute,
        auditLogsRoute,
        auditLogDetailRoute,
        reportsRoute,
        etlRoute,
        uiDemoRoute,
        notFoundRoute,
    ]),
]);

export const router = createRouter({
    routeTree,
});

declare module '@tanstack/react-router' {
    interface Register {
        router: typeof router;
    }
}
