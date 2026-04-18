import { useState } from 'react';
import { useParams, useNavigate } from '@tanstack/react-router';
import { useCase, useAssignCase, useDecideCase } from '~/hooks/useCases';
import { useAuthStore } from '~/stores/useAuthStore';
import type { CaseStatus, CaseDecision } from '~/types/api';
import { PageHeader } from '~/components/templates/PageHeader/PageHeader';
import { DetailPageTemplate } from '~/components/templates/DetailPageTemplate/DetailPageTemplate';
import { Card } from '~/components/ui/Card/Card';
import { KeyValueRow } from '~/components/ui/KeyValueRow/KeyValueRow';
import { Badge } from '~/components/ui/Badge/Badge';
import { SectionHeader } from '~/components/ui/SectionHeader/SectionHeader';
import { Button } from '~/components/ui/Button/Button';
import { Modal } from '~/components/ui/Modal/Modal';
import { Textarea } from '~/components/ui/Textarea/Textarea';
import { LoadingSkeleton } from '~/components/ui/LoadingSkeleton/LoadingSkeleton';
import { ErrorState } from '~/components/ui/ErrorState/ErrorState';

const statusVariant: Record<CaseStatus, 'default' | 'success' | 'danger' | 'warning' | 'info' | 'muted'> = {
    OPEN: 'info',
    ASSIGNED: 'warning',
    APPROVED: 'success',
    REJECTED: 'danger',
    CLOSED: 'muted',
};

export function CaseDetailPage() {
    const { caseId } = useParams({ strict: false }) as { caseId: string };
    const navigate = useNavigate();
    const user = useAuthStore((s) => s.user);
    const { data: caseData, isLoading, isError, refetch } = useCase(caseId);
    const assignCase = useAssignCase();
    const decideCase = useDecideCase();

    const [decisionModal, setDecisionModal] = useState<{ open: boolean; decision: CaseDecision | null }>({
        open: false,
        decision: null,
    });
    const [decisionNote, setDecisionNote] = useState('');

    if (isLoading) return <LoadingSkeleton variant="card" />;
    if (isError || !caseData) return <ErrorState onRetry={refetch} />;

    const isReviewer = user?.role === 'REVIEWER';
    const canAssign = isReviewer && caseData.case_status === 'OPEN';
    const canDecide = isReviewer && caseData.case_status === 'ASSIGNED' && caseData.assigned_to === user?.user_id;

    const handleAssign = () => {
        assignCase.mutate(caseId);
    };

    const handleDecision = () => {
        if (!decisionModal.decision || !decisionNote.trim()) return;
        decideCase.mutate(
            {
                caseId,
                decision: decisionModal.decision,
                decision_note: decisionNote,
                version: caseData.version,
            },
            {
                onSuccess: () => {
                    setDecisionModal({ open: false, decision: null });
                    setDecisionNote('');
                },
            },
        );
    };

    return (
        <>
            <DetailPageTemplate
                header={
                    <PageHeader
                        title={`Case ${caseData.case_id.slice(0, 8)}...`}
                        subtitle={`Created ${new Date(caseData.created_at).toLocaleString()}`}
                        actions={
                            <div className="flex items-center gap-2">
                                {canAssign && (
                                    <Button onClick={handleAssign} loading={assignCase.isPending}>
                                        Assign to Me
                                    </Button>
                                )}
                                {canDecide && (
                                    <>
                                        <Button
                                            variant="primary"
                                            onClick={() => setDecisionModal({ open: true, decision: 'APPROVE' })}
                                        >
                                            Approve
                                        </Button>
                                        <Button
                                            variant="danger"
                                            onClick={() => setDecisionModal({ open: true, decision: 'REJECT' })}
                                        >
                                            Reject
                                        </Button>
                                    </>
                                )}
                                <Button variant="ghost" onClick={() => navigate({ to: '/cases' })}>
                                    Back to List
                                </Button>
                            </div>
                        }
                    />
                }
                summary={
                    <div className="flex flex-col gap-5">
                        <div className="flex flex-col gap-1">
                            <span className="text-xs font-medium text-text-secondary">
                                Transaction Amount
                            </span>
                            <span className="text-lg font-semibold">
                                {caseData.transaction.amount.toLocaleString()}
                            </span>
                        </div>
                        <div className="flex flex-col gap-1">
                            <span className="text-xs font-medium text-text-secondary">Fraud Score</span>
                            <span className="text-lg font-semibold">
                                {(caseData.transaction.fraud_score * 100).toFixed(1)}%
                            </span>
                        </div>
                        <div className="flex flex-col gap-1">
                            <span className="text-xs font-medium text-text-secondary">Case Status</span>
                            <Badge variant={statusVariant[caseData.case_status]}>{caseData.case_status}</Badge>
                        </div>
                        <div className="flex flex-col gap-1">
                            <span className="text-xs font-medium text-text-secondary">Decision</span>
                            <span className="text-sm font-medium">{caseData.decision ?? 'Pending'}</span>
                        </div>
                    </div>
                }
                info={
                    <Card>
                        <SectionHeader title="Case Details" />
                        <div className="flex flex-col gap-1 mt-4">
                            <KeyValueRow
                                label="Case ID"
                                value={<span className="font-mono text-xs">{caseData.case_id}</span>}
                            />
                            <KeyValueRow
                                label="Transaction ID"
                                value={<span className="font-mono text-xs">{caseData.txn_id}</span>}
                            />
                            <KeyValueRow
                                label="Status"
                                value={
                                    <Badge variant={statusVariant[caseData.case_status]}>{caseData.case_status}</Badge>
                                }
                            />
                            <KeyValueRow label="Assigned To" value={caseData.assigned_to ?? 'Unassigned'} />
                            <KeyValueRow label="Decision" value={caseData.decision ?? '-'} />
                            <KeyValueRow label="Decision Note" value={caseData.decision_note ?? '-'} />
                            <KeyValueRow label="Version" value={String(caseData.version)} />
                            <KeyValueRow
                                label="Decided At"
                                value={caseData.decided_at ? new Date(caseData.decided_at).toLocaleString() : '-'}
                            />
                        </div>

                        <SectionHeader title="Transaction Info" className="mt-6" />
                        <div className="flex flex-col gap-1 mt-4">
                            <KeyValueRow
                                label="Customer ID"
                                value={<span className="font-mono text-xs">{caseData.transaction.customer_id}</span>}
                            />
                            <KeyValueRow
                                label="Merchant ID"
                                value={<span className="font-mono text-xs">{caseData.transaction.merchant_id}</span>}
                            />
                            <KeyValueRow label="Amount" value={caseData.transaction.amount.toLocaleString()} />
                            <KeyValueRow
                                label="Fraud Score"
                                value={`${(caseData.transaction.fraud_score * 100).toFixed(1)}%`}
                            />
                            <KeyValueRow
                                label="Transaction Time"
                                value={new Date(caseData.transaction.txn_time).toLocaleString()}
                            />
                        </div>
                    </Card>
                }
            />

            {/* Decision Modal */}
            <Modal
                isOpen={decisionModal.open}
                onClose={() => setDecisionModal({ open: false, decision: null })}
                title={`${decisionModal.decision === 'APPROVE' ? 'Approve' : 'Reject'} Case`}
                footer={
                    <div className="flex justify-end gap-2">
                        <Button variant="ghost" onClick={() => setDecisionModal({ open: false, decision: null })}>
                            Cancel
                        </Button>
                        <Button
                            variant={decisionModal.decision === 'APPROVE' ? 'primary' : 'danger'}
                            onClick={handleDecision}
                            loading={decideCase.isPending}
                        >
                            Confirm {decisionModal.decision === 'APPROVE' ? 'Approval' : 'Rejection'}
                        </Button>
                    </div>
                }
            >
                <Textarea
                    label="Decision Note (required)"
                    placeholder="Provide your reasoning..."
                    value={decisionNote}
                    onChange={(e) => setDecisionNote(e.target.value)}
                />
                {decideCase.isError && (
                    <p className="text-xs text-status-danger mt-2">
                        Failed to submit decision. This may be a version conflict (409) — please refresh and try again.
                    </p>
                )}
            </Modal>
        </>
    );
}
