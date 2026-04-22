import { apiClient } from './apiClient';
import type {
    ThresholdListResponse,
    ThresholdUpdateRequest,
    SuppressionRule,
    SuppressionRuleCreateRequest,
    FraudModelPerformance,
    LoanModelPerformance,
    AnalystReport,
    AnalystReportSummary,
    AnalystReportCreateRequest,
    AnalystReportAcknowledgeRequest,
} from '~/types/api';
import type { AnalystReportSearchParams } from '~/types/searchParams';

export const analystService = {
    getThresholds() {
        return apiClient.get<unknown, ThresholdListResponse>('/analyst/thresholds');
    },

    updateThresholds(data: ThresholdUpdateRequest) {
        return apiClient.patch<unknown, ThresholdListResponse>('/analyst/thresholds', data);
    },

    getFraudPerformance(days = 30) {
        return apiClient.get<unknown, FraudModelPerformance>('/analyst/model-performance/fraud', { params: { days } });
    },

    getLoanPerformance(days = 30) {
        return apiClient.get<unknown, LoanModelPerformance>('/analyst/model-performance/loan', { params: { days } });
    },

    getSuppressionRules(includeInactive = false) {
        return apiClient.get<unknown, SuppressionRule[]>('/analyst/suppression-rules', {
            params: { include_inactive: includeInactive },
        });
    },

    createSuppressionRule(data: SuppressionRuleCreateRequest) {
        return apiClient.post<unknown, SuppressionRule>('/analyst/suppression-rules', data);
    },

    disableSuppressionRule(ruleId: string) {
        return apiClient.patch<unknown, SuppressionRule>(`/analyst/suppression-rules/${ruleId}`, {});
    },

    getReports(params: AnalystReportSearchParams) {
        return apiClient.get<unknown, { total: number; limit: number; offset: number; items: AnalystReportSummary[] }>(
            '/analyst/reports',
            { params: { ...params, offset: (params.page - 1) * params.limit } },
        );
    },

    getReport(reportId: string) {
        return apiClient.get<unknown, AnalystReport>(`/analyst/reports/${reportId}`);
    },

    createReport(data: AnalystReportCreateRequest) {
        return apiClient.post<unknown, AnalystReport>('/analyst/reports', data);
    },

    acknowledgeReport(reportId: string, data: AnalystReportAcknowledgeRequest) {
        return apiClient.patch<unknown, AnalystReport>(`/analyst/reports/${reportId}/acknowledge`, data);
    },

    getReportPdfUrl(reportId: string) {
        return `/api/v1/analyst/reports/${reportId}/pdf`;
    },
};
