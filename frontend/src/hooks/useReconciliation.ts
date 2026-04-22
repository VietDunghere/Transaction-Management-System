import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { reconciliationService } from '~/services/reconciliationService';
import { toastSuccessWithActivity } from '~/utils/toastActivity';
import type { ReconciliationSearchParams } from '~/types/searchParams';
import type { ReconciliationRunRequest } from '~/types/api';

export const reconciliationKeys = {
    all: ['reconciliation'] as const,
    list: (params: ReconciliationSearchParams) => ['reconciliation', 'list', params] as const,
    detail: (id: string) => ['reconciliation', 'detail', id] as const,
};

export function useReconciliationRuns(params: ReconciliationSearchParams) {
    return useQuery({
        queryKey: reconciliationKeys.list(params),
        queryFn: () => reconciliationService.getRuns(params),
    });
}

export function useReconciliationRun(runId: string) {
    return useQuery({
        queryKey: reconciliationKeys.detail(runId),
        queryFn: () => reconciliationService.getRun(runId),
        enabled: !!runId,
    });
}

export function useTriggerReconciliation() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (data: ReconciliationRunRequest) => reconciliationService.triggerRun(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: reconciliationKeys.all });
            toastSuccessWithActivity('Reconciliation job triggered');
        },
        onError: (error: unknown) => {
            const msg = (error as any)?.response?.data?.message;
            toast.error(msg || 'Failed to trigger reconciliation');
        },
    });
}
