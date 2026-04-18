import { useState } from 'react';
import { useNavigate } from '@tanstack/react-router';
import { useCases } from '~/hooks/useCases';
import type { CaseSearchParams } from '~/types/searchParams';
import type { CaseStatus } from '~/types/api';
import { PageHeader } from '~/components/templates/PageHeader/PageHeader';
import { ListPageTemplate } from '~/components/templates/ListPageTemplate/ListPageTemplate';
import { TableShell } from '~/components/ui/TableShell/TableShell';
import { FilterBar } from '~/components/ui/FilterBar/FilterBar';
import { Select } from '~/components/ui/Select/Select';
import { Pagination } from '~/components/ui/Pagination/Pagination';
import { Badge } from '~/components/ui/Badge/Badge';
import { LoadingSkeleton } from '~/components/ui/LoadingSkeleton/LoadingSkeleton';
import { ErrorState } from '~/components/ui/ErrorState/ErrorState';
import { EmptyState } from '~/components/ui/EmptyState/EmptyState';

const statusVariant: Record<CaseStatus, 'default' | 'success' | 'danger' | 'warning' | 'info' | 'muted'> = {
    OPEN: 'info',
    ASSIGNED: 'warning',
    APPROVED: 'success',
    REJECTED: 'danger',
    CLOSED: 'muted',
};

const statusOptions = [
    { label: 'All Status', value: '' },
    { label: 'Open', value: 'OPEN' },
    { label: 'Assigned', value: 'ASSIGNED' },
    { label: 'Approved', value: 'APPROVED' },
    { label: 'Rejected', value: 'REJECTED' },
    { label: 'Closed', value: 'CLOSED' },
];

const columns = [
    { key: 'case_id', label: 'Case ID', width: '180px' },
    { key: 'txn_amount', label: 'Txn Amount', align: 'right' as const },
    { key: 'fraud_score', label: 'Fraud Score', align: 'right' as const },
    { key: 'case_status', label: 'Status' },
    { key: 'assigned_to', label: 'Assigned To' },
    { key: 'created_at', label: 'Created' },
];

export function CaseListPage() {
    const navigate = useNavigate();

    const [params, setParams] = useState<CaseSearchParams>({
        page: 1,
        limit: 20,
    });

    const { data, isLoading, isError, refetch } = useCases(params);

    const rows = (data?.data ?? []).map((c) => ({
        case_id: <span className="text-xs font-mono">{c.case_id.slice(0, 8)}...</span>,
        txn_amount: <span className="text-sm font-medium">{c.transaction.amount.toLocaleString()}</span>,
        fraud_score: <span className="text-sm">{(c.transaction.fraud_score * 100).toFixed(1)}%</span>,
        case_status: <Badge variant={statusVariant[c.case_status]}>{c.case_status}</Badge>,
        assigned_to: (
            <span className="text-xs text-text-secondary">
                {c.assigned_to ? c.assigned_to.slice(0, 8) + '...' : 'Unassigned'}
            </span>
        ),
        created_at: (
            <span className="text-xs text-text-secondary">
                {new Date(c.created_at).toLocaleString()}
            </span>
        ),
    }));

    const totalPages = data ? Math.ceil(data.total / data.limit) : 0;

    return (
        <ListPageTemplate
            header={<PageHeader title="Cases" subtitle={data ? `${data.total} total cases` : undefined} />}
            filterBar={
                <FilterBar>
                    <Select
                        options={statusOptions}
                        value={params.case_status ?? ''}
                        onChange={(e) =>
                            setParams((p) => ({
                                ...p,
                                case_status: (e.target.value || undefined) as CaseStatus | undefined,
                                page: 1,
                            }))
                        }
                        placeholder="All Status"
                    />
                </FilterBar>
            }
            table={
                isLoading ? (
                    <LoadingSkeleton variant="table" rows={8} />
                ) : isError ? (
                    <ErrorState onRetry={refetch} />
                ) : rows.length === 0 ? (
                    <EmptyState title="No cases found" description="Try adjusting your filters." />
                ) : (
                    <TableShell
                        columns={columns}
                        data={rows}
                        onRowClick={(_row, idx) => {
                            const c = data!.data[idx];
                            navigate({ to: '/cases/$caseId', params: { caseId: c.case_id } });
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
