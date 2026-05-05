import { apiClient } from './apiClient';
import type { Loan, LoanDetail, LoanDecisionRequest, LoanDecisionResponse, PagedResponse } from '~/types/api';
import type { LoanSearchParams } from '~/types/searchParams';

export const loanService = {
    getLoans(params: LoanSearchParams) {
        return apiClient.get<unknown, PagedResponse<Loan>>('/loans', { params });
    },

    getLoan(loanId: string) {
        return apiClient.get<unknown, LoanDetail>(`/loans/${loanId}`);
    },

    decideLoan(loanId: string, data: LoanDecisionRequest) {
        return apiClient.patch<unknown, LoanDecisionResponse>(`/loans/${loanId}/decision`, data);
    },

    createLoan(data: Record<string, unknown>) {
        return apiClient.post<unknown, Loan>('/loans', data);
    },

    simulateLoan(data: Record<string, unknown>) {
        return apiClient.post<unknown, { pd_score: number; risk_level: string; top_risk_factors: string[]; model_version: string }>(
            '/loans/simulate',
            data,
        );
    },
};
