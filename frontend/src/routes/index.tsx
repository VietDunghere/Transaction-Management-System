import { Outlet, createRootRoute, createRoute, createRouter } from '@tanstack/react-router';
import { DefaultLayout } from '~/layouts/DefaultLayout';
import { PublicHomePage, TestPage, UIDemoPage } from '~/pages';

const rootRoute = createRootRoute({
    component: () => (
        <DefaultLayout>
            <Outlet />
        </DefaultLayout>
    ),
});

/* ---- Public routes ---- */

const publicHomeRoute = createRoute({
    getParentRoute: () => rootRoute,
    path: '/',
    component: PublicHomePage,
});

const publicTestRoute = createRoute({
    getParentRoute: () => rootRoute,
    path: '/test',
    component: TestPage,
});

/* ---- UI Demo (internal) ---- */

const uiDemoRoute = createRoute({
    getParentRoute: () => rootRoute,
    path: '/ui-demo',
    component: UIDemoPage,
});

/* ---- Module placeholder routes (for 5 modules) ---- */

const transactionsRoute = createRoute({
    getParentRoute: () => rootRoute,
    path: '/transactions',
    component: () => (
        <div className="flex items-center justify-center h-64">
            <p className="text-2xl font-bold text-[#a3a3a3]">
                UC03 — Transaction Management
            </p>
        </div>
    ),
});

const casesRoute = createRoute({
    getParentRoute: () => rootRoute,
    path: '/cases',
    component: () => (
        <div className="flex items-center justify-center h-64">
            <p className="text-2xl font-bold text-[#a3a3a3]">
                UC05 — Case Management & Audit
            </p>
        </div>
    ),
});

const reportsRoute = createRoute({
    getParentRoute: () => rootRoute,
    path: '/reports',
    component: () => (
        <div className="flex items-center justify-center h-64">
            <p className="text-2xl font-bold text-[#a3a3a3]">
                UC06 — Reports & BI
            </p>
        </div>
    ),
});

const reconciliationRoute = createRoute({
    getParentRoute: () => rootRoute,
    path: '/reconciliation',
    component: () => (
        <div className="flex items-center justify-center h-64">
            <p className="text-2xl font-bold text-[#a3a3a3]">
                UC07 — State History & Reconciliation
            </p>
        </div>
    ),
});

/* ---- Route tree ---- */

const routeTree = rootRoute.addChildren([
    publicHomeRoute,
    publicTestRoute,
    uiDemoRoute,
    transactionsRoute,
    casesRoute,
    reportsRoute,
    reconciliationRoute,
]);

export const router = createRouter({
    routeTree,
});

declare module '@tanstack/react-router' {
    interface Register {
        router: typeof router;
    }
}
