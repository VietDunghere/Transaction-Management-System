import { apiClient } from './apiClient';
import type {
    Transaction,
    TransactionDetail,
    TransactionSubmitRequest,
    TransactionSubmitResponse,
    StateHistoryEntry,
    PagedResponse,
} from '~/types/api';
import type { TransactionSearchParams } from '~/types/searchParams';

export const transactionService = {
    getTransactions(params: TransactionSearchParams) {
        return apiClient.get<unknown, PagedResponse<Transaction>>('/transactions', { params });
    },

    getTransaction(txnId: string) {
        return apiClient.get<unknown, TransactionDetail>(`/transactions/${txnId}`);
    },

    submitTransaction(data: TransactionSubmitRequest) {
        return apiClient.post<unknown, TransactionSubmitResponse>('/transactions/submit', data);
    },

    getTransactionStates(txnId: string) {
        return apiClient.get<unknown, StateHistoryEntry[]>(`/transactions/${txnId}/state-history`);
    },
};
