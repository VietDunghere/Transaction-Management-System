import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { analystService } from '~/services/analystService';
import { toastSuccessWithActivity } from '~/utils/toastActivity';
import type { AnalystReportSearchParams } from '~/types/searchParams';
import type {
    ThresholdUpdateRequest,
    SuppressionRuleCreateRequest,
    AnalystReportCreateRequest,
    AnalystReportAcknowledgeRequest,
} from '~/types/api';

export const analystKeys = {
    all: ['analyst'] as const,
    thresholds: () => ['analyst', 'thresholds'] as const,
    fraudPerf: (days: number) => ['analyst', 'perf', 'fraud', days] as const,
    loanPerf: (days: number) => ['analyst', 'perf', 'loan', days] as const,
    rules: (includeInactive: boolean) => ['analyst', 'rules', includeInactive] as const,
    reports: (params: AnalystReportSearchParams) => ['analyst', 'reports', params] as const,
    report: (id: string) => ['analyst', 'report', id] as const,
};

export function useThresholds() {
    return useQuery({ queryKey: analystKeys.thresholds(), queryFn: () => analystService.getThresholds() });
}

export function useUpdateThresholds() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (data: ThresholdUpdateRequest) => analystService.updateThresholds(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: analystKeys.thresholds() });
            toastSuccessWithActivity('Thresholds updated successfully');
        },
        onError: (error: unknown) => {
            const msg = (error as any)?.response?.data?.message;
            toast.error(msg || 'Failed to update thresholds');
        },
    });
}

export function useFraudPerformance(days = 30) {
    return useQuery({ queryKey: analystKeys.fraudPerf(days), queryFn: () => analystService.getFraudPerformance(days) });
}

export function useLoanPerformance(days = 30) {
    return useQuery({ queryKey: analystKeys.loanPerf(days), queryFn: () => analystService.getLoanPerformance(days) });
}

export function useSuppressionRules(includeInactive = false) {
    return useQuery({
        queryKey: analystKeys.rules(includeInactive),
        queryFn: () => analystService.getSuppressionRules(includeInactive),
    });
}

export function useCreateSuppressionRule() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (data: SuppressionRuleCreateRequest) => analystService.createSuppressionRule(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['analyst', 'rules'] });
            toastSuccessWithActivity('Suppression rule created');
        },
        onError: (error: unknown) => {
            const msg = (error as any)?.response?.data?.message;
            toast.error(msg || 'Failed to create rule');
        },
    });
}

export function useDisableSuppressionRule() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (ruleId: string) => analystService.disableSuppressionRule(ruleId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['analyst', 'rules'] });
            toastSuccessWithActivity('Suppression rule disabled');
        },
        onError: (error: unknown) => {
            const msg = (error as any)?.response?.data?.message;
            toast.error(msg || 'Failed to disable rule');
        },
    });
}

export function useAnalystReports(params: AnalystReportSearchParams) {
    return useQuery({
        queryKey: analystKeys.reports(params),
        queryFn: () => analystService.getReports(params),
    });
}

export function useAnalystReport(reportId: string) {
    return useQuery({
        queryKey: analystKeys.report(reportId),
        queryFn: () => analystService.getReport(reportId),
        enabled: !!reportId,
    });
}

export function useCreateAnalystReport() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (data: AnalystReportCreateRequest) => analystService.createReport(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['analyst', 'reports'] });
            toastSuccessWithActivity('Report created successfully');
        },
        onError: (error: unknown) => {
            const msg = (error as any)?.response?.data?.message;
            toast.error(msg || 'Failed to create report');
        },
    });
}

export function useAcknowledgeReport() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ reportId, data }: { reportId: string; data: AnalystReportAcknowledgeRequest }) =>
            analystService.acknowledgeReport(reportId, data),
        onSuccess: (_data, { reportId }) => {
            queryClient.invalidateQueries({ queryKey: analystKeys.report(reportId) });
            queryClient.invalidateQueries({ queryKey: ['analyst', 'reports'] });
            toastSuccessWithActivity('Report acknowledged');
        },
        onError: (error: unknown) => {
            const msg = (error as any)?.response?.data?.message;
            toast.error(msg || 'Failed to acknowledge report');
        },
    });
}
