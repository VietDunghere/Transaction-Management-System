import { useState } from 'react';
import { useNavigate } from '@tanstack/react-router';
import { useAnalystReports, useCreateAnalystReport } from '~/hooks/useAnalyst';
import { useAuthStore } from '~/stores/useAuthStore';
import type { AnalystReportSearchParams } from '~/types/searchParams';
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
import { Textarea } from '~/components/ui/Textarea/Textarea';
import { LoadingSkeleton } from '~/components/ui/LoadingSkeleton/LoadingSkeleton';
import { ErrorState } from '~/components/ui/ErrorState/ErrorState';
import { EmptyState } from '~/components/ui/EmptyState/EmptyState';

const statusVariant: Record<string, 'info' | 'warning' | 'success' | 'muted'> = {
    DRAFT: 'muted',
    PENDING_REVIEW: 'warning',
    ACKNOWLEDGED: 'success',
};

const reportTypeOptions = [
    { label: 'All Types', value: '' },
    { label: 'Fraud Analysis', value: 'FRAUD_ANALYSIS' },
    { label: 'Loan Analysis', value: 'LOAN_ANALYSIS' },
    { label: 'Threshold Recommendation', value: 'THRESHOLD_RECOMMENDATION' },
    { label: 'Suppression Review', value: 'SUPPRESSION_REVIEW' },
    { label: 'General', value: 'GENERAL' },
];

const statusOptions = [
    { label: 'All Statuses', value: '' },
    { label: 'Draft', value: 'DRAFT' },
    { label: 'Pending Review', value: 'PENDING_REVIEW' },
    { label: 'Acknowledged', value: 'ACKNOWLEDGED' },
];

const columns = [
    { key: 'title', label: 'Title' },
    { key: 'report_type', label: 'Type' },
    { key: 'status', label: 'Status' },
    { key: 'submitted_by', label: 'Author' },
    { key: 'submitted_at', label: 'Created' },
    { key: 'acknowledged_by', label: 'Acknowledged By' },
];

export function AnalystReportsListPage() {
    const navigate = useNavigate();
    const role = useAuthStore((s) => s.user?.role);
    const canCreate = role === 'ANALYST';

    const [params, setParams] = useState<AnalystReportSearchParams>({ page: 1, limit: 20 });
    const { data, isLoading, isError, refetch } = useAnalystReports(params);
    const createReport = useCreateAnalystReport();

    const [createModal, setCreateModal] = useState(false);
    const [form, setForm] = useState({ title: '', report_type: 'GENERAL', content_md: '' });

    function handleCreate() {
        createReport.mutate(form, {
            onSuccess: (report) => {
                setCreateModal(false);
                navigate({ to: '/analyst/reports/$reportId', params: { reportId: report.report_id } });
            },
        });
    }

    const items = data?.items ?? [];
    const totalPages = data ? Math.ceil(data.total / params.limit) : 0;

    const rows = items.map((r) => ({
        title: <span className="font-medium text-sm">{r.title}</span>,
        report_type: <Badge variant="info">{r.report_type.replace(/_/g, ' ')}</Badge>,
        status: <Badge variant={statusVariant[r.status] ?? 'muted'}>{r.status.replace(/_/g, ' ')}</Badge>,
        submitted_by: <span className="text-sm text-text-secondary">{r.submitted_by}</span>,
        submitted_at: <span className="text-xs text-text-secondary">{new Date(r.submitted_at).toLocaleDateString()}</span>,
        acknowledged_by: (
            <span className="text-xs text-text-secondary">{r.acknowledged_by ?? '—'}</span>
        ),
    }));

    return (
        <>
            <ListPageTemplate
                header={
                    <PageHeader
                        title="Analyst Reports"
                        subtitle={data ? `${data.total} total reports` : undefined}
                        actions={
                            canCreate ? (
                                <Button onClick={() => setCreateModal(true)}>New Report</Button>
                            ) : undefined
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
                        <Select
                            options={reportTypeOptions}
                            value={params.report_type ?? ''}
                            onChange={(e) => setParams((p) => ({ ...p, report_type: e.target.value || undefined, page: 1 }))}
                        />
                    </FilterBar>
                }
                table={
                    isLoading ? (
                        <LoadingSkeleton variant="table" rows={8} />
                    ) : isError ? (
                        <ErrorState onRetry={refetch} />
                    ) : rows.length === 0 ? (
                        <EmptyState title="No reports found" description="Create a new analyst report." />
                    ) : (
                        <TableShell
                            columns={columns}
                            data={rows}
                            onRowClick={(_row, idx) =>
                                navigate({ to: '/analyst/reports/$reportId', params: { reportId: items[idx].report_id } })
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
                isOpen={createModal}
                onClose={() => setCreateModal(false)}
                title="New Analyst Report"
                size="lg"
                footer={
                    <div className="flex justify-end gap-2">
                        <Button variant="ghost" onClick={() => setCreateModal(false)}>Cancel</Button>
                        <Button onClick={handleCreate} loading={createReport.isPending}>Create</Button>
                    </div>
                }
            >
                <div className="flex flex-col gap-4">
                    <Input
                        label="Title (min 5 chars)"
                        placeholder="Report title"
                        value={form.title}
                        onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
                    />
                    <Select
                        label="Report Type"
                        options={reportTypeOptions.slice(1)}
                        value={form.report_type}
                        onChange={(e) => setForm((f) => ({ ...f, report_type: e.target.value }))}
                    />
                    <Textarea
                        label="Content (Markdown, min 20 chars)"
                        placeholder="# Report Title&#10;&#10;## Summary&#10;..."
                        value={form.content_md}
                        onChange={(e) => setForm((f) => ({ ...f, content_md: e.target.value }))}
                    />
                    {createReport.isError && (
                        <p className="text-xs text-status-danger">Failed to create report. Please try again.</p>
                    )}
                </div>
            </Modal>
        </>
    );
}
