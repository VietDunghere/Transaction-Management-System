import { Outlet, createRootRoute, createRoute, createRouter } from '@tanstack/react-router';
import { DefaultLayout } from '~/layouts/DefaultLayout';
import { PublicHomePage, TestPage } from '~/pages';

const rootRoute = createRootRoute({
    component: () => (
        <DefaultLayout>
            <Outlet />
        </DefaultLayout>
    ),
});

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

const routeTree = rootRoute.addChildren([publicHomeRoute, publicTestRoute]);

export const router = createRouter({
    routeTree,
});

declare module '@tanstack/react-router' {
    interface Register {
        router: typeof router;
    }
}
