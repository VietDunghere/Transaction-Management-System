import { useState } from 'react';
import { useNavigate } from '@tanstack/react-router';
import { useReconciliationRuns, useTriggerReconciliation } from '~/hooks/useReconciliation';
import type { ReconciliationSearchParams } from '~/types/searchParams';
import { PageHeader } from '~/components/templates/PageHeader/PageHeader';
import { ListPageTemplate } from '~/components/templates/ListPageTemplate/ListPageTemplate';
import { TableShell } from '~/components/ui/TableShell/TableShell';
import { FilterBar } from '~/components/ui/FilterBar/FilterBar';
import { Select } from '~/components/ui/Select/Select';
import { Pagination } from '~/components/ui/Pagination/Pagination';
import { Badge } from '~/components/ui/Badge/Badge';
import { Button } from '~/components/ui/Button/Button';
import { Modal } from '~/components/ui/Modal/Modal';
import { Input } from '~/components/ui/Input/Input';
import { LoadingSkeleton } from '~/components/ui/LoadingSkeleton/LoadingSkeleton';
import { ErrorState } from '~/components/ui/ErrorState/ErrorState';
import { EmptyState } from '~/components/ui/EmptyState/EmptyState';

const statusVariant: Record<string, 'info' | 'success' | 'danger' | 'warning'> = {
    RUNNING: 'info',
    COMPLETED: 'success',
    FAILED: 'danger',
    PENDING: 'warning',
};

const statusOptions = [
    { label: 'All Statuses', value: '' },
    { label: 'Running', value: 'RUNNING' },
    { label: 'Completed', value: 'COMPLETED' },
    { label: 'Failed', value: 'FAILED' },
];

const columns = [
    { key: 'run_id', label: 'Run ID', width: '140px' },
    { key: 'period', label: 'Period' },
    { key: 'status', label: 'Status' },
    { key: 'discrepancy_count', label: 'Discrepancies', align: 'right' as const },
    { key: 'matched_count', label: 'Matched', align: 'right' as const },
    { key: 'triggered_by', label: 'Triggered By' },
    { key: 'created_at', label: 'Created' },
];

export function ReconciliationPage() {
    const navigate = useNavigate();
    const [params, setParams] = useState<ReconciliationSearchParams>({ page: 1, limit: 20 });
    const { data, isLoading, isError, refetch } = useReconciliationRuns(params);
    const triggerRun = useTriggerReconciliation();

    const now = new Date();
    const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    const [runModal, setRunModal] = useState(false);
    const [form, setForm] = useState({
        period_start: sevenDaysAgo.toISOString().slice(0, 16),
        period_end: now.toISOString().slice(0, 16),
        pending_timeout_minutes: 120,
    });

    function handleTrigger() {
        triggerRun.mutate(
            {
                period_start: form.period_start + ':00Z',
                period_end: form.period_end + ':00Z',
                pending_timeout_minutes: Number(form.pending_timeout_minutes),
            },
            { onSuccess: () => setRunModal(false) },
        );
    }

    const runs = data?.data ?? [];
    const rows = runs.map((run) => ({
        run_id: <span className="font-mono text-xs">{run.run_id.slice(0, 8)}...</span>,
        period: (
            <span className="text-xs text-text-secondary">
                {new Date(run.period_start).toLocaleDateString()} – {new Date(run.period_end).toLocaleDateString()}
            </span>
        ),
        status: <Badge variant={statusVariant[run.status] ?? 'muted'}>{run.status}</Badge>,
        discrepancy_count: (
            <span className={`font-mono text-sm ${(run.discrepancy_count ?? 0) > 0 ? 'text-status-danger' : ''}`}>
                {run.discrepancy_count ?? '—'}
            </span>
        ),
        matched_count: <span className="font-mono text-sm">{run.matched_count ?? '—'}</span>,
        triggered_by: <span className="text-xs text-text-secondary">{run.triggered_by ?? '—'}</span>,
        created_at: <span className="text-xs text-text-secondary">{new Date(run.created_at).toLocaleString()}</span>,
    }));

    const totalPages = data ? Math.ceil(data.total / data.limit) : 0;

    return (
        <>
            <ListPageTemplate
                header={
                    <PageHeader
                        title="Reconciliation"
                        subtitle={data ? `${data.total} total runs` : undefined}
                        actions={
                            <Button onClick={() => setRunModal(true)}>Run Reconciliation</Button>
                        }
                    />
                }
                filterBar={
                    <FilterBar>
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
                        <EmptyState title="No reconciliation runs" description="Trigger a run to check for PENDING_TIMEOUT transactions." />
                    ) : (
                        <TableShell
                            columns={columns}
                            data={rows}
                            onRowClick={(_row, idx) =>
                                navigate({ to: '/reconciliation/$runId', params: { runId: runs[idx].run_id } })
                            }
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

            <Modal
                isOpen={runModal}
                onClose={() => setRunModal(false)}
                title="Trigger Reconciliation"
                footer={
                    <div className="flex justify-end gap-2">
                        <Button variant="ghost" onClick={() => setRunModal(false)}>Cancel</Button>
                        <Button onClick={handleTrigger} loading={triggerRun.isPending}>Run</Button>
                    </div>
                }
            >
                <div className="flex flex-col gap-4">
                    <Input
                        label="Period Start"
                        type="datetime-local"
                        value={form.period_start}
                        onChange={(e) => setForm((f) => ({ ...f, period_start: e.target.value }))}
                    />
                    <Input
                        label="Period End"
                        type="datetime-local"
                        value={form.period_end}
                        onChange={(e) => setForm((f) => ({ ...f, period_end: e.target.value }))}
                    />
                    <Input
                        label="Pending Timeout (minutes)"
                        type="number"
                        min="1"
                        max="10080"
                        value={String(form.pending_timeout_minutes)}
                        onChange={(e) => setForm((f) => ({ ...f, pending_timeout_minutes: Number(e.target.value) }))}
                        hint="Transactions PENDING beyond this threshold will be flagged."
                    />
                    {triggerRun.isError && (
                        <p className="text-xs text-status-danger">Failed to trigger run. Please try again.</p>
                    )}
                </div>
            </Modal>
        </>
    );
}
