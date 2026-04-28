import '@testing-library/jest-dom/vitest';
import type { ReactNode } from 'react';
import { afterEach, beforeEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';
import { useAuthStore } from '~/stores/useAuthStore';
import { useUIStore } from '~/stores/useUIStore';
import { resetRouteState } from './routerState';

vi.mock('@tanstack/react-router', async () => {
    const actual = await vi.importActual<typeof import('@tanstack/react-router')>('@tanstack/react-router');
    const { navigateMock, getRouteParams } = await import('./routerState');

    return {
        ...actual,
        useNavigate: () => navigateMock,
        useParams: () => getRouteParams(),
        Navigate: ({ to }: { to: string }) => <div data-testid="navigate" data-to={to} />,
    };
});

vi.mock('echarts-for-react', () => ({
    default: ({ option }: { option: unknown }) => <div data-testid="echarts" data-option={JSON.stringify(option)} />,
}));

vi.mock('recharts', () => ({
    ResponsiveContainer: ({ children }: { children: ReactNode }) => (
        <div data-testid="recharts-responsive">{children}</div>
    ),
    PieChart: ({ children }: { children: ReactNode }) => <div data-testid="recharts-pie-chart">{children}</div>,
    Pie: ({ children }: { children: ReactNode }) => <div data-testid="recharts-pie">{children}</div>,
    BarChart: ({ children }: { children: ReactNode }) => <div data-testid="recharts-bar-chart">{children}</div>,
    Bar: ({ children }: { children: ReactNode }) => <div data-testid="recharts-bar">{children}</div>,
    XAxis: () => null,
    YAxis: () => null,
    CartesianGrid: () => null,
    Tooltip: () => null,
    Legend: () => null,
    Cell: () => null,
}));

vi.mock('../pages/LoginPage/GeometricBackground', () => ({
    GeometricBackground: () => <div data-testid="geometric-background" />,
}));

vi.mock('../pages/LoginPage/CosmicBackground', () => ({
    CosmicBackground: () => <div data-testid="cosmic-background" />,
}));

beforeEach(() => {
    vi.clearAllMocks();
    resetRouteState();
    useAuthStore.setState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
    });
    useUIStore.setState({
        sidebarCollapsed: false,
        theme: 'light',
    });
    document.documentElement.setAttribute('data-theme', 'light');
    localStorage.clear();
});

afterEach(() => {
    cleanup();
});
