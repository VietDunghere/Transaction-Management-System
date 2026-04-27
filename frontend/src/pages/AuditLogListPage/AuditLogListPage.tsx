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
    Auth: 'info',
};

const eventVariant: Record<string, 'success' | 'danger' | 'warning' | 'info' | 'muted'> = {
    TRANSACTION_SUBMITTED: 'info',
    CASE_ASSIGNED: 'warning',
    CASE_APPROVED: 'success',
    CASE_REJECTED: 'danger',
    LOAN_APPLIED: 'info',
    LOAN_APPROVED: 'success',
    LOAN_REJECTED: 'danger',
    USER_CREATED: 'success',
    USER_DISABLED: 'danger',
    USER_ENABLED: 'success',
    USER_ROLE_UPDATED: 'warning',
    THRESHOLD_UPDATED: 'muted',
    LOGIN_SUCCESS: 'success',
    LOGIN_FAILED: 'danger',
    LOGOUT: 'info',
    PASSWORD_CHANGED: 'warning',
};

const entityTypeOptions = [
    { label: 'All Entities', value: '' },
    { label: 'Transaction', value: 'Transaction' },
    { label: 'User', value: 'User' },
    { label: 'Review Case', value: 'ReviewCase' },
    { label: 'Loan', value: 'Loan' },
    { label: 'Auth', value: 'Auth' },
];

const eventTypeOptions = [
    { label: 'All Events', value: '' },
    { label: 'Transaction Submitted', value: 'TRANSACTION_SUBMITTED' },
    { label: 'Case Assigned', value: 'CASE_ASSIGNED' },
    { label: 'Case Approved', value: 'CASE_APPROVED' },
    { label: 'Case Rejected', value: 'CASE_REJECTED' },
    { label: 'Loan Applied', value: 'LOAN_APPLIED' },
    { label: 'Loan Approved', value: 'LOAN_APPROVED' },
    { label: 'Loan Rejected', value: 'LOAN_REJECTED' },
    { label: 'User Created', value: 'USER_CREATED' },
    { label: 'User Disabled', value: 'USER_DISABLED' },
    { label: 'User Enabled', value: 'USER_ENABLED' },
    { label: 'Role Updated', value: 'USER_ROLE_UPDATED' },
    { label: 'Threshold Updated', value: 'THRESHOLD_UPDATED' },
    { label: 'Login Success', value: 'LOGIN_SUCCESS' },
    { label: 'Login Failed', value: 'LOGIN_FAILED' },
    { label: 'Logout', value: 'LOGOUT' },
    { label: 'Password Changed', value: 'PASSWORD_CHANGED' },
];

function formatRelativeTime(dateStr: string): string {
    const now = Date.now();
    const then = new Date(dateStr).getTime();
    const diff = now - then;
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'just now';
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    const days = Math.floor(hrs / 24);
    if (days < 7) return `${days}d ago`;
    return new Date(dateStr).toLocaleDateString();
}

const columns = [
    { key: 'timestamp', label: 'Time', width: '100px' },
    { key: 'event_type', label: 'Event', width: '200px' },
    { key: 'entity', label: 'Entity', width: '220px' },
    { key: 'actor', label: 'Actor' },
];

export function AuditLogListPage() {
    const navigate = useNavigate();

    const [params, setParams] = useState<AuditLogSearchParams>({
        page: 1,
        limit: 20,
    });

    const { data, isLoading, isError, refetch } = useAuditLogs(params);

    const rows = (data?.data ?? []).map((log) => ({
        timestamp: (
            <span className="text-xs font-mono text-text-secondary" title={new Date(log.event_ts).toLocaleString()}>
                {formatRelativeTime(log.event_ts)}
            </span>
        ),
        event_type: <Badge variant={eventVariant[log.event_type] ?? 'muted'}>{log.event_type}</Badge>,
        entity: (
            <div className="flex items-center gap-2">
                <Badge variant={entityVariant[log.entity_type]}>{log.entity_type}</Badge>
                <span className="text-xs font-mono text-text-tertiary">{log.entity_id.slice(0, 8)}</span>
            </div>
        ),
        actor: (
            <span className="text-sm">
                {log.actor_name ?? (
                    <span className="text-text-tertiary font-mono text-xs">
                        {log.actor_user_id?.slice(0, 8) ?? '—'}
                    </span>
                )}
            </span>
        ),
    }));

    const totalPages = data ? Math.ceil(data.total / data.limit) : 0;

    return (
        <ListPageTemplate
            header={<PageHeader title="Audit Logs" subtitle={data ? `${data.total} total entries` : undefined} />}
            filterBar={
                <FilterBar>
                    <Select
                        options={eventTypeOptions}
                        value={params.event_type ?? ''}
                        onChange={(e) =>
                            setParams((p) => ({
                                ...p,
                                event_type: e.target.value || undefined,
                                page: 1,
                            }))
                        }
                        placeholder="All Events"
                    />
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
