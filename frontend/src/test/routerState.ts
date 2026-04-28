import { vi } from 'vitest';

export const navigateMock = vi.fn();

let routeParams: Record<string, string> = {};

export function setRouteParams(nextParams: Record<string, string>) {
    routeParams = { ...nextParams };
}

export function getRouteParams() {
    return routeParams;
}

export function resetRouteState() {
    navigateMock.mockReset();
    routeParams = {};
}
