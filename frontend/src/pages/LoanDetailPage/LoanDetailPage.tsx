import { useState } from 'react';
import { useParams, useNavigate } from '@tanstack/react-router';
import { useLoan, useDecideLoan } from '~/hooks/useLoans';
import { useAuthStore } from '~/stores/useAuthStore';
import type { LoanStatus, RiskLevel, LoanDecision } from '~/types/api';
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

const statusVariant: Record<LoanStatus, 'success' | 'danger' | 'warning' | 'info' | 'muted'> = {
    APPROVED: 'success',
    REJECTED: 'danger',
    MANUAL_REVIEW: 'warning',
    PENDING: 'info',
    SCORING: 'muted',
};

const riskVariant: Record<RiskLevel, 'success' | 'warning' | 'danger'> = {
    'LOW RISK': 'success',
    'MEDIUM RISK': 'warning',
    'HIGH RISK': 'danger',
};

export function LoanDetailPage() {
    const { loanId } = useParams({ strict: false }) as { loanId: string };
    const navigate = useNavigate();
    const user = useAuthStore((s) => s.user);
    const { data: loan, isLoading, isError, refetch } = useLoan(loanId);
    const decideLoan = useDecideLoan();

    const [decisionModal, setDecisionModal] = useState<{ open: boolean; decision: LoanDecision | null }>({
        open: false,
        decision: null,
    });
    const [reviewNote, setReviewNote] = useState('');

    if (isLoading) return <LoadingSkeleton variant="card" />;
    if (isError || !loan) return <ErrorState onRetry={refetch} />;

    const canDecide =
        (user?.role === 'MANAGER' || user?.role === 'ADMIN') &&
        (loan.status === 'MANUAL_REVIEW' || loan.status === 'PENDING');

    const handleDecision = () => {
        if (!decisionModal.decision || !reviewNote.trim()) return;
        decideLoan.mutate(
            {
                loanId,
                decision: decisionModal.decision,
                review_note: reviewNote,
                version: 0, // Server manages versioning
            },
            {
                onSuccess: () => {
                    setDecisionModal({ open: false, decision: null });
                    setReviewNote('');
                },
            },
        );
    };

    return (
        <>
            <DetailPageTemplate
                header={
                    <PageHeader
                        title={`Loan ${loan.loan_id.slice(0, 8)}...`}
                        subtitle={`Created ${new Date(loan.created_at).toLocaleString()}`}
                        actions={
                            <div className="flex items-center gap-2">
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
                                <Button variant="ghost" onClick={() => navigate({ to: '/loans' })}>
                                    Back to List
                                </Button>
                            </div>
                        }
                    />
                }
                summary={
                    <div className="flex flex-col gap-5">
                        <div className="flex flex-col gap-1">
                            <span className="text-xs font-medium text-text-secondary">Principal</span>
                            <span className="text-lg font-semibold">
                                {loan.principal_amount.toLocaleString()} {loan.currency_code}
                            </span>
                        </div>
                        <div className="flex flex-col gap-1">
                            <span className="text-xs font-medium text-text-secondary">
                                Interest Rate
                            </span>
                            <span className="text-lg font-semibold">{loan.interest_rate}%</span>
                        </div>
                        <div className="flex flex-col gap-1">
                            <span className="text-xs font-medium text-text-secondary">Term</span>
                            <span className="text-lg font-semibold">{loan.term_months} months</span>
                        </div>
                        <div className="flex flex-col gap-1">
                            <span className="text-xs font-medium text-text-secondary">PD Score</span>
                            <span className="text-lg font-semibold">
                                {loan.pd_score !== null ? `${(loan.pd_score * 100).toFixed(1)}%` : '—'}
                            </span>
                        </div>
                    </div>
                }
                info={
                    <Card>
                        <SectionHeader title="Loan Details" />
                        <div className="flex flex-col gap-1 mt-4">
                            <KeyValueRow
                                label="Loan ID"
                                value={<span className="font-mono text-xs">{loan.loan_id}</span>}
                            />
                            <KeyValueRow
                                label="Customer ID"
                                value={<span className="font-mono text-xs">{loan.customer_id}</span>}
                            />
                            <KeyValueRow
                                label="Status"
                                value={<Badge variant={statusVariant[loan.status]}>{loan.status}</Badge>}
                            />
                            <KeyValueRow
                                label="Risk Level"
                                value={
                                    loan.risk_level ? (
                                        <Badge variant={riskVariant[loan.risk_level]}>{loan.risk_level}</Badge>
                                    ) : (
                                        '—'
                                    )
                                }
                            />
                            <KeyValueRow
                                label="Principal"
                                value={`${loan.principal_amount.toLocaleString()} ${loan.currency_code}`}
                            />
                            <KeyValueRow label="Interest Rate" value={`${loan.interest_rate}%`} />
                            <KeyValueRow label="Term" value={`${loan.term_months} months`} />
                            <KeyValueRow label="Purpose" value={loan.purpose} />
                            <KeyValueRow
                                label="PD Score"
                                value={loan.pd_score !== null ? `${(loan.pd_score * 100).toFixed(1)}%` : '—'}
                            />
                            <KeyValueRow
                                label="Monthly Payment"
                                value={
                                    loan.monthly_payment !== null
                                        ? `${loan.monthly_payment.toLocaleString()} ${loan.currency_code}`
                                        : '—'
                                }
                            />
                            <KeyValueRow
                                label="Maturity Date"
                                value={loan.maturity_date ? new Date(loan.maturity_date).toLocaleDateString() : '—'}
                            />
                            <KeyValueRow label="Reviewed By" value={loan.reviewed_by ?? '—'} />
                            <KeyValueRow
                                label="Reviewed At"
                                value={loan.reviewed_at ? new Date(loan.reviewed_at).toLocaleString() : '—'}
                            />
                            <KeyValueRow label="Created At" value={new Date(loan.created_at).toLocaleString()} />
                        </div>
                    </Card>
                }
            />

            {/* Decision Modal */}
            <Modal
                isOpen={decisionModal.open}
                onClose={() => setDecisionModal({ open: false, decision: null })}
                title={`${decisionModal.decision === 'APPROVE' ? 'Approve' : 'Reject'} Loan`}
                footer={
                    <div className="flex justify-end gap-2">
                        <Button variant="ghost" onClick={() => setDecisionModal({ open: false, decision: null })}>
                            Cancel
                        </Button>
                        <Button
                            variant={decisionModal.decision === 'APPROVE' ? 'primary' : 'danger'}
                            onClick={handleDecision}
                            loading={decideLoan.isPending}
                        >
                            Confirm {decisionModal.decision === 'APPROVE' ? 'Approval' : 'Rejection'}
                        </Button>
                    </div>
                }
            >
                <Textarea
                    label="Review Note (required)"
                    placeholder="Provide your reasoning..."
                    value={reviewNote}
                    onChange={(e) => setReviewNote(e.target.value)}
                />
                {decideLoan.isError && (
                    <p className="text-xs text-status-danger mt-2">
                        Failed to submit decision. Please try again.
                    </p>
                )}
            </Modal>
        </>
    );
}
