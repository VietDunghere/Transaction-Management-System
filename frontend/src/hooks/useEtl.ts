import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { etlService } from '~/services/etlService';
import type { EtlLogSearchParams } from '~/types/searchParams';
import type { TriggerEtlRequest } from '~/types/api';

export const etlKeys = {
    all: ['etl'] as const,
    list: (params: EtlLogSearchParams) => ['etl', 'list', params] as const,
};

export function useEtlLogs(params: EtlLogSearchParams) {
    return useQuery({
        queryKey: etlKeys.list(params),
        queryFn: () => etlService.getEtlLogs(params),
    });
}

export function useTriggerEtl() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (data: TriggerEtlRequest) => etlService.triggerEtl(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: etlKeys.all });
        },
    });
}
