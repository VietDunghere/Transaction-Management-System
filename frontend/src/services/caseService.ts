import { apiClient } from './apiClient';
import type {
    CaseListItem,
    CaseDetail,
    AssignCaseResponse,
    CaseDecisionRequest,
    CaseDecisionResponse,
    PagedResponse,
} from '~/types/api';
import type { CaseSearchParams } from '~/types/searchParams';

export const caseService = {
    getCases(params: CaseSearchParams) {
        return apiClient.get<unknown, PagedResponse<CaseListItem>>('/cases', { params });
    },

    getCase(caseId: string) {
        return apiClient.get<unknown, CaseDetail>(`/cases/${caseId}`);
    },

    assignCase(caseId: string) {
        return apiClient.post<unknown, AssignCaseResponse>(`/cases/${caseId}/assign`);
    },

    decideCase(caseId: string, data: CaseDecisionRequest) {
        return apiClient.patch<unknown, CaseDecisionResponse>(`/cases/${caseId}/decision`, data);
    },
};
