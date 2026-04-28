import { vi } from 'vitest';
import { useAuthStore } from '~/stores/useAuthStore';
import { useUIStore } from '~/stores/useUIStore';
import type { User } from '~/types/api';
import { navigateMock, resetRouteState, setRouteParams } from './routerState';

type MutationCallbacks<TData, TVariables> = {
    onSuccess?: (data: TData, variables: TVariables) => void;
    onError?: (error: unknown) => void;
};

export function createQueryResult<T>(data: T, overrides: Record<string, unknown> = {}) {
    return {
        data,
        isLoading: false,
        isError: false,
        refetch: vi.fn(),
        ...overrides,
    };
}

export function createMutationResult<TData = unknown, TVariables = unknown>(
    options: {
        data?: TData;
        error?: unknown;
        isPending?: boolean;
        isSuccess?: boolean;
        isError?: boolean;
        onMutate?: (variables: TVariables) => void;
    } = {},
) {
    const mutate = vi.fn((variables: TVariables, callbacks?: MutationCallbacks<TData, TVariables>) => {
        options.onMutate?.(variables);

        if (options.error !== undefined) {
            callbacks?.onError?.(options.error);
            return;
        }

        callbacks?.onSuccess?.(options.data as TData, variables);
    });

    return {
        mutate,
        isPending: options.isPending ?? false,
        isSuccess: options.isSuccess ?? false,
        isError: options.isError ?? false,
        data: options.data,
        error: options.error,
    };
}

export function setAuthUser(user: User | null) {
    useAuthStore.setState({
        user,
        isAuthenticated: Boolean(user),
        isLoading: false,
    });
}

export function setTheme(theme: 'light' | 'dark') {
    useUIStore.setState({ theme });
    document.documentElement.setAttribute('data-theme', theme);
}

export function resetTestState() {
    vi.clearAllMocks();
    resetRouteState();
    setAuthUser(null);
    useUIStore.setState({ sidebarCollapsed: false, theme: 'light' });
    document.documentElement.setAttribute('data-theme', 'light');
    localStorage.clear();
}

export { navigateMock, resetRouteState, setRouteParams };
