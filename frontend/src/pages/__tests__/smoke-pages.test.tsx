import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { LoginPage } from '~/pages/LoginPage/LoginPage';
import { DashboardPage } from '~/pages/DashboardPage/DashboardPage';
import { ForbiddenPage } from '~/pages/ForbiddenPage/ForbiddenPage';
import { NotFoundPage } from '~/pages/NotFoundPage/NotFoundPage';
import { adminUser, dashboardSummary, fraudTrend, reviewerUser } from '~/test/fixtures';
import {
    createMutationResult,
    createQueryResult,
    navigateMock,
    setAuthUser,
    setRouteParams,
    setTheme,
} from '~/test/testUtils';

const authHookMocks = vi.hoisted(() => ({
    useLogin: vi.fn(),
}));

const dashboardHookMocks = vi.hoisted(() => ({
    useDashboardSummary: vi.fn(),
    useFraudTrend: vi.fn(),
}));

vi.mock('~/hooks/useAuth', () => ({
    useLogin: authHookMocks.useLogin,
}));

vi.mock('~/hooks/useDashboard', () => ({
    useDashboardSummary: dashboardHookMocks.useDashboardSummary,
    useFraudTrend: dashboardHookMocks.useFraudTrend,
}));

describe('auth and shell pages', () => {
    beforeEach(() => {
        setTheme('light');
        setRouteParams({});
    });

    it('renders the login form and submits credentials', async () => {
        const user = userEvent.setup();
        const loginMutation = createMutationResult();
        authHookMocks.useLogin.mockReturnValue(loginMutation);
        setAuthUser(null);

        render(<LoginPage />);

        expect(screen.getByRole('heading', { name: 'Login To Your Account' })).toBeInTheDocument();
        expect(screen.getByLabelText('Username')).toBeInTheDocument();
        expect(screen.getByLabelText('Password')).toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'Login' })).toBeInTheDocument();
        expect(screen.getByTestId('geometric-background')).toBeInTheDocument();

        await user.type(screen.getByLabelText('Username'), 'demo.user');
        await user.type(screen.getByLabelText('Password'), 'secret123');
        await user.click(screen.getByRole('button', { name: 'Login' }));

        expect(loginMutation.mutate).toHaveBeenCalledWith({
            username: 'demo.user',
            password: 'secret123',
        });
    });

    it('redirects authenticated users from the login page', () => {
        authHookMocks.useLogin.mockReturnValue(createMutationResult());
        setAuthUser(adminUser);

        render(<LoginPage />);

        expect(screen.getAllByTestId('navigate').some((node) => node.getAttribute('data-to') === '/')).toBe(true);
    });

    it('shows the dashboard overview and chart state', () => {
        dashboardHookMocks.useDashboardSummary.mockReturnValue(createQueryResult(dashboardSummary));
        dashboardHookMocks.useFraudTrend.mockReturnValue(createQueryResult({ data: fraudTrend }));
        setAuthUser(null);

        render(<DashboardPage />);

        expect(screen.getByRole('heading', { name: 'Dashboard' })).toBeInTheDocument();
        expect(screen.getByText('System overview and fraud monitoring')).toBeInTheDocument();
        expect(screen.getByText('Fraud Trend (Last 30 Days)')).toBeInTheDocument();
        expect(screen.getByText('Transactions by Status')).toBeInTheDocument();
        expect(screen.getByText('Loans & Cases')).toBeInTheDocument();
        expect(screen.getByText('1,234')).toBeInTheDocument();
        expect(screen.getByText('48')).toBeInTheDocument();
        expect(screen.getByTestId('echarts')).toBeInTheDocument();
    });

    it('redirects privileged dashboard roles to their landing page', () => {
        dashboardHookMocks.useDashboardSummary.mockReturnValue(createQueryResult(dashboardSummary));
        dashboardHookMocks.useFraudTrend.mockReturnValue(createQueryResult({ data: fraudTrend }));
        setAuthUser(reviewerUser);

        render(<DashboardPage />);

        expect(screen.getAllByTestId('navigate').some((node) => node.getAttribute('data-to') === '/cases')).toBe(
            true,
        );
    });

    it('renders forbidden and not found fallbacks', async () => {
        const user = userEvent.setup();

        render(<ForbiddenPage />);
        expect(screen.getByText('403')).toBeInTheDocument();
        await user.click(screen.getByRole('button', { name: 'Go to Dashboard' }));
        expect(navigateMock).toHaveBeenLastCalledWith({ to: '/' });

        navigateMock.mockClear();

        render(<NotFoundPage />);
        expect(screen.getByText('404')).toBeInTheDocument();
        await user.click(screen.getAllByRole('button', { name: 'Go to Dashboard' }).at(-1)!);
        expect(navigateMock).toHaveBeenLastCalledWith({ to: '/' });
    });
});
