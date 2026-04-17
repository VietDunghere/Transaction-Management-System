import { useState } from 'react';
import { useNavigate } from '@tanstack/react-router';
import { useTransactions } from '~/hooks/useTransactions';
import { useAuthStore } from '~/stores/useAuthStore';
import type { TransactionSearchParams } from '~/types/searchParams';
import type { TransactionStatus } from '~/types/api';
import { PageHeader } from '~/components/templates/PageHeader/PageHeader';
import { ListPageTemplate } from '~/components/templates/ListPageTemplate/ListPageTemplate';
import { TableShell } from '~/components/ui/TableShell/TableShell';
import { FilterBar } from '~/components/ui/FilterBar/FilterBar';
import { Select } from '~/components/ui/Select/Select';
import { DateRangeShell } from '~/components/ui/DateRangeShell/DateRangeShell';
import { Pagination } from '~/components/ui/Pagination/Pagination';
import { Badge } from '~/components/ui/Badge/Badge';
import { Button } from '~/components/ui/Button/Button';
import { LoadingSkeleton } from '~/components/ui/LoadingSkeleton/LoadingSkeleton';
import { ErrorState } from '~/components/ui/ErrorState/ErrorState';
import { EmptyState } from '~/components/ui/EmptyState/EmptyState';

const statusVariant: Record<TransactionStatus, 'success' | 'danger' | 'warning' | 'info'> = {
    APPROVED: 'success',
    REJECTED: 'danger',
    MANUAL_REVIEW: 'warning',
    PENDING: 'info',
};

const statusOptions = [
    { label: 'All Status', value: '' },
    { label: 'Pending', value: 'PENDING' },
    { label: 'Approved', value: 'APPROVED' },
    { label: 'Rejected', value: 'REJECTED' },
    { label: 'Manual Review', value: 'MANUAL_REVIEW' },
];

const columns = [
    { key: 'txn_id', label: 'Transaction ID', width: '220px' },
    { key: 'amount', label: 'Amount', align: 'right' as const },
    { key: 'status', label: 'Status' },
    { key: 'fraud_score', label: 'Fraud Score', align: 'right' as const },
    { key: 'txn_time', label: 'Time' },
];

export function TransactionListPage() {
    const navigate = useNavigate();
    const userRole = useAuthStore((s) => s.user?.role);

    const [params, setParams] = useState<TransactionSearchParams>({
        page: 1,
        limit: 20,
    });

    const { data, isLoading, isError, refetch } = useTransactions(params);

    const rows = (data?.data ?? []).map((txn) => ({
        txn_id: <span className="text-xs font-mono">{txn.txn_id.slice(0, 8)}...</span>,
        amount: (
            <span className="text-sm font-medium">
                {txn.amount.toLocaleString()} {txn.currency_code}
            </span>
        ),
        status: <Badge variant={statusVariant[txn.status]}>{txn.status}</Badge>,
        fraud_score: <span className="text-sm">{(txn.fraud_score * 100).toFixed(1)}%</span>,
        txn_time: (
            <span className="text-xs text-[var(--color-text-secondary)]">
                {new Date(txn.txn_time).toLocaleString()}
            </span>
        ),
    }));

    const totalPages = data ? Math.ceil(data.total / data.limit) : 0;

    return (
        <ListPageTemplate
            header={
                <PageHeader
                    title="Transactions"
                    subtitle={data ? `${data.total} total transactions` : undefined}
                    actions={
                        userRole === 'OPERATOR' ? (
                            <Button onClick={() => navigate({ to: '/transactions/submit' })}>Submit Transaction</Button>
                        ) : undefined
                    }
                />
            }
            filterBar={
                <FilterBar>
                    <Select
                        options={statusOptions}
                        value={params.status ?? ''}
                        onChange={(e) =>
                            setParams((p) => ({
                                ...p,
                                status: (e.target.value || undefined) as TransactionStatus | undefined,
                                page: 1,
                            }))
                        }
                        placeholder="All Status"
                    />
                    <DateRangeShell
                        startValue={params.from_date}
                        endValue={params.to_date}
                        onStartChange={(v) => setParams((p) => ({ ...p, from_date: v || undefined, page: 1 }))}
                        onEndChange={(v) => setParams((p) => ({ ...p, to_date: v || undefined, page: 1 }))}
                    />
                </FilterBar>
            }
            table={
                isLoading ? (
                    <LoadingSkeleton variant="table" rows={8} />
                ) : isError ? (
                    <ErrorState onRetry={refetch} />
                ) : rows.length === 0 ? (
                    <EmptyState title="No transactions found" description="Try adjusting your filters." />
                ) : (
                    <TableShell
                        columns={columns}
                        data={rows}
                        onRowClick={(_row, idx) => {
                            const txn = data!.data[idx];
                            navigate({ to: '/transactions/$txnId', params: { txnId: txn.txn_id } });
                        }}
                    />
                )
            }
            pagination={
                totalPages > 1 ? (
                    <Pagination
                        currentPage={params.page}
                        totalPages={totalPages}
                        onPageChange={(page) => setParams((p) => ({ ...p, page }))}
                    />
                ) : undefined
            }
        />
    );
}
