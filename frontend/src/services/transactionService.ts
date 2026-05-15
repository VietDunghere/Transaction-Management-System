import { apiClient } from './apiClient';
import type { Transaction, TransactionDetail, PagedResponse } from '~/types/api';
import type { TransactionSearchParams } from '~/types/searchParams';

export const transactionService = {
    getTransactions(params: TransactionSearchParams) {
        return apiClient.get<unknown, PagedResponse<Transaction>>('/transactions', { params });
    },

    getTransaction(txnId: string) {
        return apiClient.get<unknown, TransactionDetail>(`/transactions/${txnId}`);
    },


    submitTransaction(data: Record<string, unknown>) {
        return apiClient.post<unknown, { txn_id: string; status: string; fraud_score: number; decision: string; amount: number; case_id: string | null; message: string }>(
            '/transactions/submit',
            data,
        );
    },
};
