import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { caseService } from '~/services/caseService';
import type { CaseSearchParams } from '~/types/searchParams';
import type { CaseDecisionRequest } from '~/types/api';

export const caseKeys = {
    all: ['cases'] as const,
    list: (params: CaseSearchParams) => ['cases', 'list', params] as const,
    detail: (caseId: string) => ['cases', 'detail', caseId] as const,
};

export function useCases(params: CaseSearchParams) {
    return useQuery({
        queryKey: caseKeys.list(params),
        queryFn: () => caseService.getCases(params),
    });
}

export function useCase(caseId: string) {
    return useQuery({
        queryKey: caseKeys.detail(caseId),
        queryFn: () => caseService.getCase(caseId),
        enabled: !!caseId,
    });
}

export function useAssignCase() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (caseId: string) => caseService.assignCase(caseId),
        onSuccess: (_data, caseId) => {
            queryClient.invalidateQueries({ queryKey: caseKeys.detail(caseId) });
            queryClient.invalidateQueries({ queryKey: caseKeys.all });
        },
    });
}

export function useDecideCase() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ caseId, ...data }: CaseDecisionRequest & { caseId: string }) =>
            caseService.decideCase(caseId, data),
        onSuccess: (_data, vars) => {
            queryClient.invalidateQueries({ queryKey: caseKeys.detail(vars.caseId) });
            queryClient.invalidateQueries({ queryKey: caseKeys.all });
        },
    });
}
