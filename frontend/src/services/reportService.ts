import { apiClient } from './apiClient';
import type { TransactionReportEntry, FraudReportEntry } from '~/types/api';
import type { ReportSearchParams } from '~/types/searchParams';

export const reportService = {
    getTransactionReport(params: ReportSearchParams) {
        if (params.format === 'csv') {
            return apiClient.get<unknown, Blob>('/reports/transactions', {
                params,
                responseType: 'blob',
            });
        }
        return apiClient.get<unknown, TransactionReportEntry[]>('/reports/transactions', { params });
    },

    getFraudReport(params: ReportSearchParams) {
        if (params.format === 'csv') {
            return apiClient.get<unknown, Blob>('/reports/fraud', {
                params,
                responseType: 'blob',
            });
        }
        return apiClient.get<unknown, FraudReportEntry[]>('/reports/fraud', { params });
    },
};
