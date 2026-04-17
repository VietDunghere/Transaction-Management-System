import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { loanService } from '~/services/loanService';
import type { LoanSearchParams } from '~/types/searchParams';
import type { CreateLoanRequest, LoanSimulateRequest, LoanDecisionRequest } from '~/types/api';

export const loanKeys = {
    all: ['loans'] as const,
    list: (params: LoanSearchParams) => ['loans', 'list', params] as const,
    detail: (loanId: string) => ['loans', 'detail', loanId] as const,
};

export function useLoans(params: LoanSearchParams) {
    return useQuery({
        queryKey: loanKeys.list(params),
        queryFn: () => loanService.getLoans(params),
    });
}

export function useLoan(loanId: string) {
    return useQuery({
        queryKey: loanKeys.detail(loanId),
        queryFn: () => loanService.getLoan(loanId),
        enabled: !!loanId,
    });
}

export function useCreateLoan() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (data: CreateLoanRequest) => loanService.createLoan(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: loanKeys.all });
        },
    });
}

export function useSimulateLoan() {
    return useMutation({
        mutationFn: (data: LoanSimulateRequest) => loanService.simulateLoan(data),
    });
}

export function useDecideLoan() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ loanId, ...data }: LoanDecisionRequest & { loanId: string }) =>
            loanService.decideLoan(loanId, data),
        onSuccess: (_data, vars) => {
            queryClient.invalidateQueries({ queryKey: loanKeys.detail(vars.loanId) });
            queryClient.invalidateQueries({ queryKey: loanKeys.all });
        },
    });
}
