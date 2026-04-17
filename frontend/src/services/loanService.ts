import { apiClient } from './apiClient';
import type {
    Loan,
    LoanDetail,
    CreateLoanRequest,
    LoanSimulateRequest,
    LoanSimulateResponse,
    LoanDecisionRequest,
    LoanDecisionResponse,
    PagedResponse,
} from '~/types/api';
import type { LoanSearchParams } from '~/types/searchParams';

export const loanService = {
    getLoans(params: LoanSearchParams) {
        return apiClient.get<unknown, PagedResponse<Loan>>('/loans', { params });
    },

    getLoan(loanId: string) {
        return apiClient.get<unknown, LoanDetail>(`/loans/${loanId}`);
    },

    createLoan(data: CreateLoanRequest) {
        return apiClient.post<unknown, LoanDetail>('/loans', data);
    },

    simulateLoan(data: LoanSimulateRequest) {
        return apiClient.post<unknown, LoanSimulateResponse>('/loans/simulate', data);
    },

    decideLoan(loanId: string, data: LoanDecisionRequest) {
        return apiClient.patch<unknown, LoanDecisionResponse>(`/loans/${loanId}/decision`, data);
    },
};
