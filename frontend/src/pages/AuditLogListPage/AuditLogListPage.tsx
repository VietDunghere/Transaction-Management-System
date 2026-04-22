import { useState } from 'react';
import { useNavigate } from '@tanstack/react-router';
import { useAuditLogs } from '~/hooks/useAuditLogs';
import type { AuditLogSearchParams } from '~/types/searchParams';
import type { AuditEntityType } from '~/types/api';
import { PageHeader } from '~/components/templates/PageHeader/PageHeader';
import { ListPageTemplate } from '~/components/templates/ListPageTemplate/ListPageTemplate';
import { TableShell } from '~/components/ui/TableShell/TableShell';
import { FilterBar } from '~/components/ui/FilterBar/FilterBar';
import { Select } from '~/components/ui/Select/Select';
import { DateRangeShell } from '~/components/ui/DateRangeShell/DateRangeShell';
import { Pagination } from '~/components/ui/Pagination/Pagination';
import { Badge } from '~/components/ui/Badge/Badge';
import { LoadingSkeleton } from '~/components/ui/LoadingSkeleton/LoadingSkeleton';
import { ErrorState } from '~/components/ui/ErrorState/ErrorState';
import { EmptyState } from '~/components/ui/EmptyState/EmptyState';

const entityVariant: Record<AuditEntityType, 'info' | 'warning' | 'success' | 'danger'> = {
    Transaction: 'info',
    User: 'success',
    ReviewCase: 'warning',
    Loan: 'danger',
};

const entityTypeOptions = [
    { label: 'All Entities', value: '' },
    { label: 'Transaction', value: 'Transaction' },
    { label: 'User', value: 'User' },
    { label: 'Review Case', value: 'ReviewCase' },
    { label: 'Loan', value: 'Loan' },
];

const columns = [
    { key: 'event_type', label: 'Event', width: '180px' },
    { key: 'entity_type', label: 'Entity Type' },
    { key: 'entity_id', label: 'Entity ID', width: '150px' },
    { key: 'actor', label: 'Actor' },
    { key: 'timestamp', label: 'Timestamp' },
];

export function AuditLogListPage() {
    const navigate = useNavigate();

    const [params, setParams] = useState<AuditLogSearchParams>({
        page: 1,
        limit: 20,
    });

    const { data, isLoading, isError, refetch } = useAuditLogs(params);

    const rows = (data?.data ?? []).map((log) => ({
        event_type: <span className="text-sm font-medium">{log.event_type}</span>,
        entity_type: <Badge variant={entityVariant[log.entity_type]}>{log.entity_type}</Badge>,
        entity_id: <span className="text-xs font-mono">{log.entity_id.slice(0, 8)}...</span>,
        actor: (
            <span className="text-sm">
                {log.actor_name}{' '}
                <span className="text-xs text-text-tertiary">({log.actor_user_id.slice(0, 8)}...)</span>
            </span>
        ),
        timestamp: <span className="text-xs text-text-secondary">{new Date(log.event_ts).toLocaleString()}</span>,
    }));

    const totalPages = data ? Math.ceil(data.total / data.limit) : 0;

    return (
        <ListPageTemplate
            header={<PageHeader title="Audit Logs" subtitle={data ? `${data.total} total entries` : undefined} />}
            filterBar={
                <FilterBar>
                    <Select
                        options={entityTypeOptions}
                        value={params.entity_type ?? ''}
                        onChange={(e) =>
                            setParams((p) => ({
                                ...p,
                                entity_type: (e.target.value || undefined) as AuditEntityType | undefined,
                                page: 1,
                            }))
                        }
                        placeholder="All Entities"
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
                    <EmptyState title="No audit logs found" description="Try adjusting your filters." />
                ) : (
                    <TableShell
                        columns={columns}
                        data={rows}
                        onRowClick={(_row, idx) => {
                            const log = data!.data[idx];
                            navigate({ to: '/audit-logs/$logId', params: { logId: log.log_id } });
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
