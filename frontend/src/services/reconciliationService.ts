import { apiClient } from './apiClient';
import type { ReconciliationRun, ReconciliationDetail, ReconciliationRunRequest, PagedResponse } from '~/types/api';
import type { ReconciliationSearchParams } from '~/types/searchParams';

export const reconciliationService = {
    getRuns(params: ReconciliationSearchParams) {
        return apiClient.get<unknown, PagedResponse<ReconciliationRun>>('/reconciliation/reports', { params });
    },

    getRun(runId: string) {
        return apiClient.get<unknown, ReconciliationDetail>(`/reconciliation/${runId}`);
    },

    triggerRun(data: ReconciliationRunRequest) {
        return apiClient.post<unknown, ReconciliationRun>('/reconciliation/run', data);
    },
};
