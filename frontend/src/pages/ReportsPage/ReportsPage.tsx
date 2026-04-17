import { useState } from 'react';
import {
    useTransactionReport,
    useFraudReport,
    useExportTransactionReport,
    useExportFraudReport,
} from '~/hooks/useReports';
import type { ReportSearchParams } from '~/types/searchParams';
import { PageHeader } from '~/components/templates/PageHeader/PageHeader';
import { ListPageTemplate } from '~/components/templates/ListPageTemplate/ListPageTemplate';
import { FilterBar } from '~/components/ui/FilterBar/FilterBar';
import { DateRangeShell } from '~/components/ui/DateRangeShell/DateRangeShell';
import { TableShell } from '~/components/ui/TableShell/TableShell';
import { Button } from '~/components/ui/Button/Button';
import { Badge } from '~/components/ui/Badge/Badge';
import { LoadingSkeleton } from '~/components/ui/LoadingSkeleton/LoadingSkeleton';
import { ErrorState } from '~/components/ui/ErrorState/ErrorState';
import { EmptyState } from '~/components/ui/EmptyState/EmptyState';

type Tab = 'transactions' | 'fraud';

export function ReportsPage() {
    const [activeTab, setActiveTab] = useState<Tab>('transactions');
    const [params, setParams] = useState<ReportSearchParams>({
        format: 'json',
    });

    const txnReport = useTransactionReport(params);
    const fraudReport = useFraudReport(params);
    const exportTxn = useExportTransactionReport();
    const exportFraud = useExportFraudReport();

    const isLoading = activeTab === 'transactions' ? txnReport.isLoading : fraudReport.isLoading;
    const isError = activeTab === 'transactions' ? txnReport.isError : fraudReport.isError;
    const refetch = activeTab === 'transactions' ? txnReport.refetch : fraudReport.refetch;

    const txnColumns = [
        { key: 'txn_id', label: 'Transaction ID', width: '200px' },
        { key: 'amount', label: 'Amount', align: 'right' as const },
        { key: 'status', label: 'Status' },
        { key: 'fraud_score', label: 'Fraud Score', align: 'right' as const },
        { key: 'txn_time', label: 'Time' },
    ];

    const fraudColumns = [
        { key: 'date', label: 'Date' },
        { key: 'total_txn', label: 'Total Txn', align: 'right' as const },
        { key: 'approved', label: 'Approved', align: 'right' as const },
        { key: 'rejected', label: 'Rejected', align: 'right' as const },
        { key: 'fraud_count', label: 'Fraud Count', align: 'right' as const },
        { key: 'fraud_rate', label: 'Fraud Rate', align: 'right' as const },
    ];

    const txnRows = (txnReport.data ?? []).map((r) => ({
        txn_id: <span className="text-xs font-mono">{r.txn_id.slice(0, 8)}...</span>,
        amount: (
            <span className="text-sm">
                {r.amount.toLocaleString()} {r.currency_code}
            </span>
        ),
        status: (
            <Badge variant={r.status === 'APPROVED' ? 'success' : r.status === 'REJECTED' ? 'danger' : 'warning'}>
                {r.status}
            </Badge>
        ),
        fraud_score: <span className="text-sm">{(r.fraud_score * 100).toFixed(1)}%</span>,
        txn_time: <span className="text-xs">{new Date(r.txn_time).toLocaleString()}</span>,
    }));

    const fraudRows = (fraudReport.data ?? []).map((r) => ({
        date: <span className="text-sm">{r.date}</span>,
        total_txn: <span className="text-sm">{r.total_txn}</span>,
        approved: <span className="text-sm text-[var(--color-status-success)]">{r.approved}</span>,
        rejected: <span className="text-sm text-[var(--color-status-danger)]">{r.rejected}</span>,
        fraud_count: <span className="text-sm font-medium">{r.fraud_count}</span>,
        fraud_rate: <span className="text-sm">{(r.fraud_rate * 100).toFixed(2)}%</span>,
    }));

    return (
        <ListPageTemplate
            header={
                <PageHeader
                    title="Reports"
                    subtitle="Transaction and fraud analysis reports"
                    actions={
                        <Button
                            variant="secondary"
                            loading={activeTab === 'transactions' ? exportTxn.isPending : exportFraud.isPending}
                            onClick={() => {
                                const exportParams = { ...params };
                                delete (exportParams as Record<string, unknown>).format;
                                if (activeTab === 'transactions') exportTxn.mutate(exportParams);
                                else exportFraud.mutate(exportParams);
                            }}
                        >
                            Export CSV
                        </Button>
                    }
                />
            }
            filterBar={
                <FilterBar>
                    <div className="flex items-center gap-2">
                        <button
                            onClick={() => setActiveTab('transactions')}
                            className={`px-3 py-1.5 rounded-sm text-sm transition-colors ${
                                activeTab === 'transactions'
                                    ? 'bg-accent-indigo text-white'
                                    : 'text-[var(--color-text-secondary)] hover:bg-subtle'
                            }`}
                        >
                            Transaction Report
                        </button>
                        <button
                            onClick={() => setActiveTab('fraud')}
                            className={`px-3 py-1.5 rounded-sm text-sm transition-colors ${
                                activeTab === 'fraud'
                                    ? 'bg-accent-indigo text-white'
                                    : 'text-[var(--color-text-secondary)] hover:bg-subtle'
                            }`}
                        >
                            Fraud Report
                        </button>
                    </div>
                    <DateRangeShell
                        startValue={params.from_date}
                        endValue={params.to_date}
                        onStartChange={(v) => setParams((p) => ({ ...p, from_date: v || undefined }))}
                        onEndChange={(v) => setParams((p) => ({ ...p, to_date: v || undefined }))}
                    />
                </FilterBar>
            }
            table={
                isLoading ? (
                    <LoadingSkeleton variant="table" rows={8} />
                ) : isError ? (
                    <ErrorState onRetry={refetch} />
                ) : activeTab === 'transactions' ? (
                    txnRows.length === 0 ? (
                        <EmptyState title="No transaction data" />
                    ) : (
                        <TableShell columns={txnColumns} data={txnRows} />
                    )
                ) : fraudRows.length === 0 ? (
                    <EmptyState title="No fraud data" />
                ) : (
                    <TableShell columns={fraudColumns} data={fraudRows} />
                )
            }
        />
    );
}
