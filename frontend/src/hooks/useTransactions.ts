import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { transactionService } from '~/services/transactionService';
import { toastMutationError } from '~/utils/mutationErrorToast';
import { toastSuccessWithActivity } from '~/utils/toastActivity';
import type { TransactionSearchParams } from '~/types/searchParams';

export const transactionKeys = {
    all: ['transactions'] as const,
    list: (params: TransactionSearchParams) => ['transactions', 'list', params] as const,
    detail: (txnId: string) => ['transactions', 'detail', txnId] as const,
};

export function useTransactions(params: TransactionSearchParams, refetchInterval?: number | false) {
    return useQuery({
        queryKey: transactionKeys.list(params),
        queryFn: () => transactionService.getTransactions(params),
        refetchInterval,
    });
}

export function useTransaction(txnId: string) {
    return useQuery({
        queryKey: transactionKeys.detail(txnId),
        queryFn: () => transactionService.getTransaction(txnId),
        enabled: !!txnId,
    });
}

export function useSubmitTransaction() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (data: Record<string, unknown>) => transactionService.submitTransaction(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: transactionKeys.all });
            toastSuccessWithActivity('Transaction submitted');
        },
        onError: (error: unknown) => {
            toastMutationError(error);
        },
    });
}
