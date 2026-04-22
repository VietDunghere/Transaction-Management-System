import { useNavigate, useParams } from '@tanstack/react-router';
import { useReconciliationRun } from '~/hooks/useReconciliation';
import { PageHeader } from '~/components/templates/PageHeader/PageHeader';
import { DetailPageTemplate } from '~/components/templates/DetailPageTemplate/DetailPageTemplate';
import { Card } from '~/components/ui/Card/Card';
import { SectionHeader } from '~/components/ui/SectionHeader/SectionHeader';
import { TableShell } from '~/components/ui/TableShell/TableShell';
import { Badge } from '~/components/ui/Badge/Badge';
import { Button } from '~/components/ui/Button/Button';
import { LoadingSkeleton } from '~/components/ui/LoadingSkeleton/LoadingSkeleton';
import { ErrorState } from '~/components/ui/ErrorState/ErrorState';
import { EmptyState } from '~/components/ui/EmptyState/EmptyState';

const runStatusVariant: Record<string, 'info' | 'success' | 'danger' | 'warning'> = {
    RUNNING: 'info', COMPLETED: 'success', FAILED: 'danger', PENDING: 'warning',
};
const itemStatusVariant: Record<string, 'warning' | 'success' | 'muted'> = {
    OPEN: 'warning', RESOLVED: 'success', IGNORED: 'muted',
};

const itemColumns = [
    { key: 'txn_id', label: 'Transaction ID' },
    { key: 'item_type', label: 'Type' },
    { key: 'txn_status', label: 'Txn Status' },
    { key: 'txn_amount', label: 'Amount', align: 'right' as const },
    { key: 'minutes_pending', label: 'Pending (min)', align: 'right' as const },
    { key: 'status', label: 'Status' },
];

export function ReconciliationDetailPage() {
    const { runId } = useParams({ strict: false }) as { runId: string };
    const navigate = useNavigate();
    const { data, isLoading, isError, refetch } = useReconciliationRun(runId);

    if (isLoading) return <LoadingSkeleton variant="card" />;
    if (isError || !data) return <ErrorState onRetry={refetch} />;

    const itemRows = (data.items ?? []).map((item) => ({
        txn_id: <span className="font-mono text-xs">{item.txn_id ? item.txn_id.slice(0, 8) + '...' : '—'}</span>,
        item_type: <Badge variant="info">{item.item_type}</Badge>,
        txn_status: <span className="text-sm">{item.txn_status ?? '—'}</span>,
        txn_amount: (
            <span className="font-mono text-sm">
                {item.txn_amount != null ? item.txn_amount.toLocaleString(undefined, { maximumFractionDigits: 2 }) : '—'}
            </span>
        ),
        minutes_pending: <span className="font-mono text-sm">{item.minutes_pending ?? '—'}</span>,
        status: <Badge variant={itemStatusVariant[item.status] ?? 'muted'}>{item.status}</Badge>,
    }));

    return (
        <DetailPageTemplate
            header={
                <PageHeader
                    title={`Reconciliation Run`}
                    subtitle={`${new Date(data.period_start).toLocaleDateString()} – ${new Date(data.period_end).toLocaleDateString()}`}
                    actions={
                        <Button variant="ghost" onClick={() => navigate({ to: '/reconciliation' })}>Back</Button>
                    }
                />
            }
            summary={
                <div className="flex flex-col gap-5">
                    <div className="flex flex-col gap-1">
                        <span className="text-xs font-medium text-text-secondary">Status</span>
                        <Badge variant={runStatusVariant[data.status] ?? 'muted'}>{data.status}</Badge>
                    </div>
                    <div className="flex flex-col gap-1">
                        <span className="text-xs font-medium text-text-secondary">Discrepancies</span>
                        <span className={`text-2xl font-semibold ${(data.discrepancy_count ?? 0) > 0 ? 'text-status-danger' : ''}`}>
                            {data.discrepancy_count ?? '—'}
                        </span>
                    </div>
                    <div className="flex flex-col gap-1">
                        <span className="text-xs font-medium text-text-secondary">Matched</span>
                        <span className="text-lg font-semibold">{data.matched_count ?? '—'}</span>
                    </div>
                    <div className="flex flex-col gap-1">
                        <span className="text-xs font-medium text-text-secondary">Total Checked</span>
                        <span className="text-sm">{data.total_txn_count ?? '—'}</span>
                    </div>
                    <div className="flex flex-col gap-1">
                        <span className="text-xs font-medium text-text-secondary">Timeout Threshold</span>
                        <span className="text-sm">{data.pending_timeout_minutes} min</span>
                    </div>
                    {data.error_message && (
                        <div className="flex flex-col gap-1">
                            <span className="text-xs font-medium text-status-danger">Error</span>
                            <span className="text-xs text-status-danger">{data.error_message}</span>
                        </div>
                    )}
                </div>
            }
            info={
                <Card noPadding>
                    <div className="p-8 pb-4">
                        <SectionHeader title={`Discrepancy Items (${data.items?.length ?? 0})`} />
                    </div>
                    {itemRows.length === 0 ? (
                        <EmptyState title="No discrepancies" description="All transactions matched successfully." />
                    ) : (
                        <TableShell columns={itemColumns} data={itemRows} />
                    )}
                </Card>
            }
        />
    );
}
