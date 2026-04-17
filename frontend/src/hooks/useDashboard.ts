import { useQuery } from '@tanstack/react-query';
import { dashboardService } from '~/services/dashboardService';

export const dashboardKeys = {
    summary: ['dashboard', 'summary'] as const,
    fraudTrend: (days: number) => ['dashboard', 'fraud-trend', days] as const,
};

export function useDashboardSummary() {
    return useQuery({
        queryKey: dashboardKeys.summary,
        queryFn: () => dashboardService.getSummary(),
        staleTime: 60_000,
    });
}

export function useFraudTrend(days = 30) {
    return useQuery({
        queryKey: dashboardKeys.fraudTrend(days),
        queryFn: () => dashboardService.getFraudTrend(days),
        staleTime: 60_000,
    });
}
