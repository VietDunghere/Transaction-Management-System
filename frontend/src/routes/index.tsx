import { Outlet, createRootRoute, createRoute, createRouter, redirect } from '@tanstack/react-router';
import { DefaultLayout } from '~/layouts/DefaultLayout';
import { PublicLayout } from '~/layouts/PublicLayout';
import {
    LoginPage,
    ProfilePage,
    DashboardPage,
    TransactionListPage,
    TransactionDetailPage,
    TransactionSubmitPage,
    CaseListPage,
    CaseDetailPage,
    UserListPage,
    UserCreatePage,
    UserDetailPage,
    LoanListPage,
    LoanDetailPage,
    LoanCreatePage,
    LoanSimulatePage,
    AuditLogListPage,
    AuditLogDetailPage,
    ForbiddenPage,
    NotFoundPage,
    AnalystThresholdsPage,
    AnalystModelPerformancePage,
    DemoPage,
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

// -- Dashboard (UC05.1: ANALYST, MANAGER) --
const dashboardRoute = createRoute({
    getParentRoute: () => authLayoutRoute,
    path: '/',
    component: DashboardPage,
    beforeLoad: () => {
        const role = getUserRole();
        if (role === 'OPERATOR') throw redirect({ to: '/loans' });
        if (role === 'REVIEWER') throw redirect({ to: '/cases' });
        if (role === 'ADMIN') throw redirect({ to: '/users' });
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

// -- Transactions (UC02.2: ANALYST, MANAGER) --
const transactionsRoute = createRoute({
    getParentRoute: () => authLayoutRoute,
    path: '/transactions',
    component: TransactionListPage,
    beforeLoad: () => guardRole(['ANALYST', 'MANAGER']),
});

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
    beforeLoad: () => guardRole(['ANALYST', 'MANAGER']),
});

// -- Cases (UC04: REVIEWER) --
const casesRoute = createRoute({
    getParentRoute: () => authLayoutRoute,
    path: '/cases',
    component: CaseListPage,
    beforeLoad: () => guardRole(['REVIEWER']),
});

const caseDetailRoute = createRoute({
    getParentRoute: () => authLayoutRoute,
    path: '/cases/$caseId',
    component: CaseDetailPage,
    beforeLoad: () => guardRole(['REVIEWER']),
});

// -- Loans (UC03: OPERATOR, REVIEWER) --
const loansRoute = createRoute({
    getParentRoute: () => authLayoutRoute,
    path: '/loans',
    component: LoanListPage,
    beforeLoad: () => guardRole(['OPERATOR', 'REVIEWER']),
});

const loanCreateRoute = createRoute({
    getParentRoute: () => authLayoutRoute,
    path: '/loans/create',
    component: LoanCreatePage,
    beforeLoad: () => guardRole(['OPERATOR']),
});

const loanSimulateRoute = createRoute({
    getParentRoute: () => authLayoutRoute,
    path: '/loans/simulate',
    component: LoanSimulatePage,
    beforeLoad: () => guardRole(['OPERATOR', 'REVIEWER']),
});

const loanDetailRoute = createRoute({
    getParentRoute: () => authLayoutRoute,
    path: '/loans/$loanId',
    component: LoanDetailPage,
    beforeLoad: () => guardRole(['OPERATOR', 'REVIEWER']),
});

// -- Users (UC06: MANAGER view, ADMIN full) --
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

// -- Audit Logs (UC05.2: MANAGER, ADMIN) --
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

// -- Analyst Module (UC07: ANALYST) --
const analystThresholdsRoute = createRoute({
    getParentRoute: () => authLayoutRoute,
    path: '/analyst/thresholds',
    component: AnalystThresholdsPage,
    beforeLoad: () => guardRole(['ANALYST']),
});

// -- Demo Runner (OPERATOR only) --
const demoRoute = createRoute({
    getParentRoute: () => authLayoutRoute,
    path: '/demo',
    component: DemoPage,
    beforeLoad: () => guardRole(['OPERATOR']),
});

const analystModelPerfRoute = createRoute({
    getParentRoute: () => authLayoutRoute,
    path: '/analyst/model-performance',
    component: AnalystModelPerformancePage,
    beforeLoad: () => guardRole(['ANALYST']),
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
    publicLayoutRoute.addChildren([loginRoute]),
    authLayoutRoute.addChildren([
        dashboardRoute,
        profileRoute,
        forbiddenRoute,
        transactionsRoute,
        transactionSubmitRoute,
        transactionDetailRoute,
        casesRoute,
        caseDetailRoute,
        loansRoute,
        loanCreateRoute,
        loanSimulateRoute,
        loanDetailRoute,
        usersRoute,
        userCreateRoute,
        userDetailRoute,
        auditLogsRoute,
        auditLogDetailRoute,
        analystThresholdsRoute,
        analystModelPerfRoute,
        demoRoute,
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
