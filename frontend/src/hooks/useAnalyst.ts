import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { analystService } from '~/services/analystService';
import { toastMutationError } from '~/utils/mutationErrorToast';
import { toastSuccessWithActivity } from '~/utils/toastActivity';
import type { ThresholdUpdateRequest } from '~/types/api';

export const analystKeys = {
    all: ['analyst'] as const,
    thresholds: () => ['analyst', 'thresholds'] as const,
    fraudPerf: (days: number) => ['analyst', 'perf', 'fraud', days] as const,
    loanPerf: (days: number) => ['analyst', 'perf', 'loan', days] as const,
};

export function useThresholds() {
    return useQuery({ queryKey: analystKeys.thresholds(), queryFn: () => analystService.getThresholds() });
}

export function useUpdateThresholds() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (data: ThresholdUpdateRequest) => analystService.updateThresholds(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: analystKeys.thresholds() });
            toastSuccessWithActivity('Thresholds updated successfully');
            // Auto-clear success state after 3 seconds
            setTimeout(() => {
                // Mutation state will naturally expire via TanStack Query
            }, 3000);
        },
        onError: (error: unknown) => {
            toastMutationError(error, 'Failed to update thresholds');
        },
    });
}

export function useFraudPerformance(days = 30) {
    return useQuery({ queryKey: analystKeys.fraudPerf(days), queryFn: () => analystService.getFraudPerformance(days) });
}

export function useLoanPerformance(days = 30) {
    return useQuery({ queryKey: analystKeys.loanPerf(days), queryFn: () => analystService.getLoanPerformance(days) });
}
