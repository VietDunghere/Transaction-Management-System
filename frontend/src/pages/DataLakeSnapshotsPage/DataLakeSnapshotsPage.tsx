import { useState } from 'react';
import { useDataLakeSnapshots } from '~/hooks/useDataLake';
import type { DataLakeSearchParams } from '~/types/searchParams';
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

const columns = [
    { key: 'snapshot_id', label: 'ID', width: '160px' },
    { key: 'snapshot_type', label: 'Type' },
    { key: 'snapshot_date', label: 'Date' },
    { key: 'record_count', label: 'Records', align: 'right' as const },
    { key: 'total_amount', label: 'Total Amount', align: 'right' as const },
    { key: 'source_label', label: 'Source' },
    { key: 'status', label: 'Status' },
    { key: 'created_at', label: 'Created' },
];

const typeOptions = [
    { label: 'All Types', value: '' },
    { label: 'Daily Summary', value: 'DAILY_TXN_SUMMARY' },
    { label: 'External Ingest', value: 'EXTERNAL_INGEST' },
];

const statusOptions = [
    { label: 'All Statuses', value: '' },
    { label: 'Active', value: 'ACTIVE' },
    { label: 'Archived', value: 'ARCHIVED' },
];

export function DataLakeSnapshotsPage() {
    const [params, setParams] = useState<DataLakeSearchParams>({ page: 1, limit: 20 });
    const { data, isLoading, isError, refetch } = useDataLakeSnapshots(params);

    const rows = (data?.data ?? []).map((snap) => ({
        snapshot_id: <span className="font-mono text-xs">{snap.snapshot_id.slice(0, 8)}...</span>,
        snapshot_type: <Badge variant="info">{snap.snapshot_type.replace(/_/g, ' ')}</Badge>,
        snapshot_date: <span className="text-sm">{snap.snapshot_date}</span>,
        record_count: <span className="font-mono text-sm">{snap.record_count.toLocaleString()}</span>,
        total_amount: (
            <span className="font-mono text-sm">
                {snap.total_amount != null ? snap.total_amount.toLocaleString(undefined, { maximumFractionDigits: 2 }) : '—'}
            </span>
        ),
        source_label: <span className="text-sm text-text-secondary">{snap.source_label ?? '—'}</span>,
        status: <Badge variant={snap.status === 'ACTIVE' ? 'success' : 'muted'}>{snap.status}</Badge>,
        created_at: <span className="text-xs text-text-secondary">{new Date(snap.created_at).toLocaleString()}</span>,
    }));

    const totalPages = data ? Math.ceil(data.total / data.limit) : 0;

    return (
        <ListPageTemplate
            header={
                <PageHeader
                    title="Data Lake Snapshots"
                    subtitle={data ? `${data.total} total snapshots` : undefined}
                />
            }
            filterBar={
                <FilterBar>
                    <Select
                        options={typeOptions}
                        value={params.snapshot_type ?? ''}
                        onChange={(e) => setParams((p) => ({ ...p, snapshot_type: e.target.value || undefined, page: 1 }))}
                    />
                    <Select
                        options={statusOptions}
                        value={params.status ?? ''}
                        onChange={(e) => setParams((p) => ({ ...p, status: e.target.value || undefined, page: 1 }))}
                    />
                </FilterBar>
            }
            table={
                isLoading ? (
                    <LoadingSkeleton variant="table" rows={8} />
                ) : isError ? (
                    <ErrorState onRetry={refetch} />
                ) : rows.length === 0 ? (
                    <EmptyState title="No snapshots found" description="Run the ETL pipeline to generate daily summaries." />
                ) : (
                    <TableShell columns={columns} data={rows} />
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
