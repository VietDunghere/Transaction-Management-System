import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
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
            toast.success('ETL job triggered successfully');
        },
        onError: (error: unknown) => {
            const apiMsg = (error as any)?.response?.data?.message;
            toast.error(apiMsg || (error instanceof Error ? error.message : 'Something went wrong'));
        },
    });
}
