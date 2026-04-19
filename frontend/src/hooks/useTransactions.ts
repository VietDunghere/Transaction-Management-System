import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { transactionService } from '~/services/transactionService';
import { toastSuccessWithActivity } from '~/utils/toastActivity';
import type { TransactionSearchParams } from '~/types/searchParams';
import type { TransactionSubmitRequest } from '~/types/api';

export const transactionKeys = {
    all: ['transactions'] as const,
    list: (params: TransactionSearchParams) => ['transactions', 'list', params] as const,
    detail: (txnId: string) => ['transactions', 'detail', txnId] as const,
    states: (txnId: string) => ['transactions', 'states', txnId] as const,
};

export function useTransactions(params: TransactionSearchParams) {
    return useQuery({
        queryKey: transactionKeys.list(params),
        queryFn: () => transactionService.getTransactions(params),
    });
}

export function useTransaction(txnId: string) {
    return useQuery({
        queryKey: transactionKeys.detail(txnId),
        queryFn: () => transactionService.getTransaction(txnId),
        enabled: !!txnId,
    });
}

export function useTransactionStates(txnId: string) {
    return useQuery({
        queryKey: transactionKeys.states(txnId),
        queryFn: () => transactionService.getTransactionStates(txnId),
        enabled: !!txnId,
    });
}

export function useSubmitTransaction() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (data: TransactionSubmitRequest) => transactionService.submitTransaction(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: transactionKeys.all });
            toastSuccessWithActivity('Transaction submitted successfully');
        },
        onError: (error: unknown) => {
            const apiMsg = (error as any)?.response?.data?.message;
            toast.error(apiMsg || (error instanceof Error ? error.message : 'Something went wrong'));
        },
    });
}
