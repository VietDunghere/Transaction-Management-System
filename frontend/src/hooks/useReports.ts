import { useQuery, useMutation } from '@tanstack/react-query';
import { reportService } from '~/services/reportService';
import type { ReportSearchParams } from '~/types/searchParams';
import type { TransactionReportEntry, FraudReportEntry } from '~/types/api';

export const reportKeys = {
    transactions: (params: ReportSearchParams) => ['reports', 'transactions', params] as const,
    fraud: (params: ReportSearchParams) => ['reports', 'fraud', params] as const,
};

export function useTransactionReport(params: ReportSearchParams) {
    return useQuery({
        queryKey: reportKeys.transactions(params),
        queryFn: () =>
            reportService.getTransactionReport({ ...params, format: 'json' }) as Promise<TransactionReportEntry[]>,
    });
}

export function useFraudReport(params: ReportSearchParams) {
    return useQuery({
        queryKey: reportKeys.fraud(params),
        queryFn: () => reportService.getFraudReport({ ...params, format: 'json' }) as Promise<FraudReportEntry[]>,
    });
}

function downloadBlob(blob: Blob, filename: string) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

export function useExportTransactionReport() {
    return useMutation({
        mutationFn: (params: Omit<ReportSearchParams, 'format'>) =>
            reportService.getTransactionReport({ ...params, format: 'csv' }) as Promise<Blob>,
        onSuccess: (blob) => {
            downloadBlob(blob, `transactions_report.csv`);
        },
    });
}

export function useExportFraudReport() {
    return useMutation({
        mutationFn: (params: Omit<ReportSearchParams, 'format'>) =>
            reportService.getFraudReport({ ...params, format: 'csv' }) as Promise<Blob>,
        onSuccess: (blob) => {
            downloadBlob(blob, `fraud_report.csv`);
        },
    });
}
