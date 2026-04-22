import { useState } from 'react';
import { useNavigate, useParams } from '@tanstack/react-router';
import { useAnalystReport, useAcknowledgeReport } from '~/hooks/useAnalyst';
import { useAuthStore } from '~/stores/useAuthStore';
import { PageHeader } from '~/components/templates/PageHeader/PageHeader';
import { DetailPageTemplate } from '~/components/templates/DetailPageTemplate/DetailPageTemplate';
import { Card } from '~/components/ui/Card/Card';
import { SectionHeader } from '~/components/ui/SectionHeader/SectionHeader';
import { Badge } from '~/components/ui/Badge/Badge';
import { Button } from '~/components/ui/Button/Button';
import { Modal } from '~/components/ui/Modal/Modal';
import { Textarea } from '~/components/ui/Textarea/Textarea';
import { LoadingSkeleton } from '~/components/ui/LoadingSkeleton/LoadingSkeleton';
import { ErrorState } from '~/components/ui/ErrorState/ErrorState';
import { analystService } from '~/services/analystService';

const statusVariant: Record<string, 'info' | 'warning' | 'success' | 'muted'> = {
    DRAFT: 'muted',
    PENDING_REVIEW: 'warning',
    ACKNOWLEDGED: 'success',
};

export function AnalystReportDetailPage() {
    const { reportId } = useParams({ strict: false }) as { reportId: string };
    const navigate = useNavigate();
    const role = useAuthStore((s) => s.user?.role);
    const canAcknowledge = role === 'MANAGER' || role === 'ADMIN';

    const { data, isLoading, isError, refetch } = useAnalystReport(reportId);
    const acknowledge = useAcknowledgeReport();

    const [ackModal, setAckModal] = useState(false);
    const [note, setNote] = useState('');

    function handleAcknowledge() {
        acknowledge.mutate({ reportId, data: { note: note || undefined } }, { onSuccess: () => setAckModal(false) });
    }

    function handleDownloadPdf() {
        const url = `${import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'}${analystService.getReportPdfUrl(reportId)}`;
        const a = document.createElement('a');
        a.href = url;
        a.download = `report_${reportId.slice(0, 8)}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }

    if (isLoading) return <LoadingSkeleton variant="card" />;
    if (isError || !data) return <ErrorState onRetry={refetch} />;

    return (
        <>
            <DetailPageTemplate
                header={
                    <PageHeader
                        title={data.title}
                        subtitle={`${data.report_type.replace(/_/g, ' ')} · ${new Date(data.submitted_at).toLocaleDateString()}`}
                        actions={
                            <div className="flex items-center gap-2">
                                <Button variant="secondary" onClick={handleDownloadPdf}>
                                    Download PDF
                                </Button>
                                {canAcknowledge && data.status === 'PENDING_REVIEW' && (
                                    <Button onClick={() => setAckModal(true)}>Acknowledge</Button>
                                )}
                                <Button variant="ghost" onClick={() => navigate({ to: '/analyst/reports' })}>
                                    Back
                                </Button>
                            </div>
                        }
                    />
                }
                summary={
                    <div className="flex flex-col gap-5">
                        <div className="flex flex-col gap-1">
                            <span className="text-xs font-medium text-text-secondary">Status</span>
                            <Badge variant={statusVariant[data.status] ?? 'muted'}>
                                {data.status.replace(/_/g, ' ')}
                            </Badge>
                        </div>
                        <div className="flex flex-col gap-1">
                            <span className="text-xs font-medium text-text-secondary">Type</span>
                            <span className="text-sm font-semibold">{data.report_type.replace(/_/g, ' ')}</span>
                        </div>
                        <div className="flex flex-col gap-1">
                            <span className="text-xs font-medium text-text-secondary">Author</span>
                            <span className="text-sm">{data.submitted_by}</span>
                        </div>
                        <div className="flex flex-col gap-1">
                            <span className="text-xs font-medium text-text-secondary">Submitted</span>
                            <span className="text-sm">{new Date(data.submitted_at).toLocaleString()}</span>
                        </div>
                        {data.acknowledged_by && (
                            <>
                                <div className="flex flex-col gap-1">
                                    <span className="text-xs font-medium text-text-secondary">Acknowledged By</span>
                                    <span className="text-sm">{data.acknowledged_by}</span>
                                </div>
                                <div className="flex flex-col gap-1">
                                    <span className="text-xs font-medium text-text-secondary">Acknowledged At</span>
                                    <span className="text-sm">
                                        {data.acknowledged_at ? new Date(data.acknowledged_at).toLocaleString() : '—'}
                                    </span>
                                </div>
                            </>
                        )}
                        {data.note && (
                            <div className="flex flex-col gap-1">
                                <span className="text-xs font-medium text-text-secondary">Manager Note</span>
                                <span className="text-sm italic text-text-secondary">{data.note}</span>
                            </div>
                        )}
                    </div>
                }
                info={
                    <Card>
                        <SectionHeader title="Report Content" />
                        <div className="mt-4 prose prose-sm max-w-none">
                            <pre className="whitespace-pre-wrap text-sm text-text-primary font-sans leading-relaxed">
                                {data.content_md}
                            </pre>
                        </div>
                    </Card>
                }
            />

            <Modal
                isOpen={ackModal}
                onClose={() => setAckModal(false)}
                title="Acknowledge Report"
                footer={
                    <div className="flex justify-end gap-2">
                        <Button variant="ghost" onClick={() => setAckModal(false)}>
                            Cancel
                        </Button>
                        <Button onClick={handleAcknowledge} loading={acknowledge.isPending}>
                            Confirm
                        </Button>
                    </div>
                }
            >
                <div className="flex flex-col gap-4">
                    <p className="text-sm text-text-secondary">
                        Confirm that you have read and reviewed this analyst report. The status will change to
                        ACKNOWLEDGED.
                    </p>
                    <Textarea
                        label="Response Note (optional)"
                        placeholder="Add a note for the analyst..."
                        value={note}
                        onChange={(e) => setNote(e.target.value)}
                    />
                    {acknowledge.isError && (
                        <p className="text-xs text-status-danger">Failed to acknowledge. Please try again.</p>
                    )}
                </div>
            </Modal>
        </>
    );
}
