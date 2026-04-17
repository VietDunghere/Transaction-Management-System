import { useState } from 'react';
import { useEtlLogs, useTriggerEtl } from '~/hooks/useEtl';
import { useAuthStore } from '~/stores/useAuthStore';
import type { EtlLogSearchParams } from '~/types/searchParams';
import type { EtlJobStatus } from '~/types/api';
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

const statusVariant: Record<EtlJobStatus, 'success' | 'danger' | 'info'> = {
    SUCCESS: 'success',
    FAILED: 'danger',
    RUNNING: 'info',
};

const statusOptions = [
    { label: 'All Status', value: '' },
    { label: 'Running', value: 'RUNNING' },
    { label: 'Success', value: 'SUCCESS' },
    { label: 'Failed', value: 'FAILED' },
];

const jobTypeOptions = [
    { label: 'All Types', value: '' },
    { label: 'daily_summary', value: 'daily_summary' },
    { label: 'fraud_aggregation', value: 'fraud_aggregation' },
];

const columns = [
    { key: 'job_id', label: 'Job ID', width: '180px' },
    { key: 'job_type', label: 'Type' },
    { key: 'target_date', label: 'Target Date' },
    { key: 'status', label: 'Status' },
    { key: 'records', label: 'Records (E/T/L)', align: 'right' as const },
    { key: 'started_at', label: 'Started' },
    { key: 'completed_at', label: 'Completed' },
];

export function EtlLogListPage() {
    const userRole = useAuthStore((s) => s.user?.role);
    const triggerEtl = useTriggerEtl();

    const [params, setParams] = useState<EtlLogSearchParams>({
        page: 1,
        limit: 20,
    });

    const [triggerModal, setTriggerModal] = useState(false);
    const [triggerDate, setTriggerDate] = useState(new Date().toISOString().slice(0, 10));
    const [triggerJobType, setTriggerJobType] = useState('daily_summary');

    const { data, isLoading, isError, refetch } = useEtlLogs(params);

    const rows = (data?.data ?? []).map((job) => ({
        job_id: <span className="text-xs font-mono">{job.job_id.slice(0, 8)}...</span>,
        job_type: <span className="text-sm">{job.job_type}</span>,
        target_date: <span className="text-sm">{job.target_date}</span>,
        status: <Badge variant={statusVariant[job.status]}>{job.status}</Badge>,
        records: (
            <span className="text-xs font-mono">
                {job.records_extracted ?? '—'} / {job.records_transformed ?? '—'} / {job.records_loaded ?? '—'}
            </span>
        ),
        started_at: (
            <span className="text-xs text-[var(--color-text-secondary)]">
                {new Date(job.started_at).toLocaleString()}
            </span>
        ),
        completed_at: (
            <span className="text-xs text-[var(--color-text-secondary)]">
                {job.completed_at ? new Date(job.completed_at).toLocaleString() : '—'}
            </span>
        ),
    }));

    const totalPages = data ? Math.ceil(data.total / data.limit) : 0;
    const isAdmin = userRole === 'ADMIN';

    const handleTrigger = () => {
        triggerEtl.mutate(
            { target_date: triggerDate, job_type: triggerJobType },
            {
                onSuccess: () => setTriggerModal(false),
            },
        );
    };

    return (
        <>
            <ListPageTemplate
                header={
                    <PageHeader
                        title="ETL Pipeline"
                        subtitle={data ? `${data.total} total jobs` : undefined}
                        actions={
                            isAdmin ? (
                                <Button onClick={() => setTriggerModal(true)}>Trigger ETL</Button>
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
                                    status: (e.target.value || undefined) as EtlJobStatus | undefined,
                                    page: 1,
                                }))
                            }
                            placeholder="All Status"
                        />
                        <Select
                            options={jobTypeOptions}
                            value={params.job_type ?? ''}
                            onChange={(e) =>
                                setParams((p) => ({
                                    ...p,
                                    job_type: e.target.value || undefined,
                                    page: 1,
                                }))
                            }
                            placeholder="All Types"
                        />
                    </FilterBar>
                }
                table={
                    isLoading ? (
                        <LoadingSkeleton variant="table" rows={8} />
                    ) : isError ? (
                        <ErrorState onRetry={refetch} />
                    ) : rows.length === 0 ? (
                        <EmptyState title="No ETL jobs found" description="Try adjusting your filters." />
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

            {/* Trigger ETL Modal */}
            <Modal
                isOpen={triggerModal}
                onClose={() => setTriggerModal(false)}
                title="Trigger ETL Job"
                footer={
                    <div className="flex justify-end gap-2">
                        <Button variant="ghost" onClick={() => setTriggerModal(false)}>
                            Cancel
                        </Button>
                        <Button onClick={handleTrigger} loading={triggerEtl.isPending}>
                            Run ETL
                        </Button>
                    </div>
                }
            >
                <div className="flex flex-col gap-4">
                    <Input
                        label="Target Date"
                        type="date"
                        value={triggerDate}
                        onChange={(e) => setTriggerDate(e.target.value)}
                    />
                    <Select
                        label="Job Type"
                        options={[
                            { label: 'Daily Summary', value: 'daily_summary' },
                            { label: 'Fraud Aggregation', value: 'fraud_aggregation' },
                        ]}
                        value={triggerJobType}
                        onChange={(e) => setTriggerJobType(e.target.value)}
                    />
                </div>
                {triggerEtl.isError && (
                    <p className="text-xs text-[var(--color-status-danger)] mt-2">
                        Failed to trigger ETL job. Please try again.
                    </p>
                )}
            </Modal>
        </>
    );
}
