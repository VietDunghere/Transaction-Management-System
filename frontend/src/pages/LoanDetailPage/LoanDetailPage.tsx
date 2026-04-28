import { useState } from 'react';
import { useParams, useNavigate } from '@tanstack/react-router';
import { useLoan, useDecideLoan } from '~/hooks/useLoans';
import { useAuthStore } from '~/stores/useAuthStore';
import type { LoanStatus, RiskLevel, LoanDecision } from '~/types/api';
import { riskLabel } from '~/types/api';
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
    PENDING: 'info',
    APPROVED: 'success',
    REJECTED: 'danger',
    DISBURSED: 'info',
    CLOSED: 'muted',
    DEFAULTED: 'danger',
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
        (user?.role === 'REVIEWER' || user?.role === 'MANAGER' || user?.role === 'ADMIN') && loan.status === 'PENDING';

    const handleDecision = () => {
        if (!decisionModal.decision || !reviewNote.trim()) return;
        decideLoan.mutate(
            {
                loanId,
                decision: decisionModal.decision,
                review_note: reviewNote,
                version: loan.version,
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
                        title="Loan Detail"
                        subtitle={`${loan.principal_amount.toLocaleString()} ${loan.currency_code} · ${loan.interest_rate}% · ${loan.term_months}mo · ${loan.risk_level ? riskLabel[loan.risk_level] : loan.status} · Created ${new Date(loan.created_at).toLocaleString()}`}
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
                main={
                    <>
                        <Card>
                            <SectionHeader title="Loan Details" />
                            <div className="flex flex-col gap-1 mt-4">
                                <KeyValueRow
                                    label="Loan ID"
                                    value={<span className="font-mono text-xs">{loan.loan_id}</span>}
                                />
                                <KeyValueRow
                                    label="Customer"
                                    value={
                                        <span>
                                            {loan.customer_name && (
                                                <span className="font-medium mr-2">{loan.customer_name}</span>
                                            )}
                                            <span className="font-mono text-xs text-text-tertiary">
                                                {loan.customer_id.slice(0, 12)}…
                                            </span>
                                        </span>
                                    }
                                />
                                <KeyValueRow
                                    label="Status"
                                    value={<Badge variant={statusVariant[loan.status]}>{loan.status}</Badge>}
                                />
                                <KeyValueRow
                                    label="Risk Level"
                                    value={
                                        loan.risk_level ? (
                                            <Badge variant={riskVariant[loan.risk_level]}>
                                                {riskLabel[loan.risk_level]}
                                            </Badge>
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
                                <KeyValueRow label="Created At" value={new Date(loan.created_at).toLocaleString()} />
                            </div>
                        </Card>

                        {(loan.person_age !== null || loan.person_income !== null || loan.loan_grade !== null) && (
                            <Card>
                                <SectionHeader title="Applicant Profile" />
                                <div className="flex flex-col gap-1 mt-4">
                                    {loan.person_age !== null && (
                                        <KeyValueRow label="Age" value={`${loan.person_age} years`} />
                                    )}
                                    {loan.person_income !== null && (
                                        <KeyValueRow
                                            label="Annual Income"
                                            value={`${loan.person_income.toLocaleString()} ${loan.currency_code}`}
                                        />
                                    )}
                                    {loan.person_home_ownership && (
                                        <KeyValueRow label="Home Ownership" value={loan.person_home_ownership} />
                                    )}
                                    {loan.person_emp_length !== null && (
                                        <KeyValueRow
                                            label="Employment Length"
                                            value={`${loan.person_emp_length} years`}
                                        />
                                    )}
                                    {loan.loan_grade && (
                                        <KeyValueRow
                                            label="Loan Grade"
                                            value={
                                                <Badge
                                                    variant={
                                                        ['A', 'B'].includes(loan.loan_grade)
                                                            ? 'success'
                                                            : ['C', 'D'].includes(loan.loan_grade)
                                                              ? 'warning'
                                                              : 'danger'
                                                    }
                                                >
                                                    {loan.loan_grade}
                                                </Badge>
                                            }
                                        />
                                    )}
                                    {loan.loan_intent && <KeyValueRow label="Loan Intent" value={loan.loan_intent} />}
                                    {loan.cb_person_default_on_file && (
                                        <KeyValueRow
                                            label="Prior Default"
                                            value={
                                                <Badge
                                                    variant={
                                                        loan.cb_person_default_on_file === 'Y' ? 'danger' : 'success'
                                                    }
                                                >
                                                    {loan.cb_person_default_on_file === 'Y' ? 'Yes' : 'No'}
                                                </Badge>
                                            }
                                        />
                                    )}
                                    {loan.cb_person_cred_hist_length !== null && (
                                        <KeyValueRow
                                            label="Credit History"
                                            value={`${loan.cb_person_cred_hist_length} years`}
                                        />
                                    )}
                                </div>
                            </Card>
                        )}
                    </>
                }
                aside={
                    <>
                        {(loan.customer_job || loan.customer_kyc_status || loan.customer_income_level) && (
                            <Card>
                                <SectionHeader title="Customer Profile" />
                                <div className="flex flex-col gap-1 mt-4">
                                    {loan.customer_job && <KeyValueRow label="Occupation" value={loan.customer_job} />}
                                    {loan.customer_kyc_status && (
                                        <KeyValueRow
                                            label="KYC Status"
                                            value={
                                                <Badge
                                                    variant={
                                                        loan.customer_kyc_status === 'VERIFIED'
                                                            ? 'success'
                                                            : loan.customer_kyc_status === 'PENDING'
                                                              ? 'warning'
                                                              : 'danger'
                                                    }
                                                >
                                                    {loan.customer_kyc_status}
                                                </Badge>
                                            }
                                        />
                                    )}
                                    {loan.customer_income_level && (
                                        <KeyValueRow label="Income Level" value={loan.customer_income_level} />
                                    )}
                                </div>
                            </Card>
                        )}

                        <Card>
                            <SectionHeader title="Review Info" />
                            <div className="flex flex-col gap-1 mt-4">
                                <KeyValueRow
                                    label="Reviewed By"
                                    value={loan.reviewer_name ?? loan.reviewed_by ?? '—'}
                                />
                                <KeyValueRow
                                    label="Reviewed At"
                                    value={loan.reviewed_at ? new Date(loan.reviewed_at).toLocaleString() : '—'}
                                />
                            </div>
                        </Card>
                    </>
                }
                fullWidth={
                    loan.customer_loan_stats ? (
                        <Card>
                            <SectionHeader title="Loan History (This Bank)" />
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4">
                                <div className="flex flex-col gap-0.5 p-3 bg-bg-secondary rounded-lg">
                                    <span className="text-xs text-text-secondary">Total Previous</span>
                                    <span className="text-lg font-semibold">
                                        {loan.customer_loan_stats.total_loans}
                                    </span>
                                </div>
                                <div className="flex flex-col gap-0.5 p-3 bg-bg-secondary rounded-lg">
                                    <span className="text-xs text-text-secondary">Approved</span>
                                    <span className="text-lg font-semibold text-status-success">
                                        {loan.customer_loan_stats.approved}
                                    </span>
                                </div>
                                <div className="flex flex-col gap-0.5 p-3 bg-bg-secondary rounded-lg">
                                    <span className="text-xs text-text-secondary">Rejected</span>
                                    <span className="text-lg font-semibold text-status-danger">
                                        {loan.customer_loan_stats.rejected}
                                    </span>
                                </div>
                                <div className="flex flex-col gap-0.5 p-3 bg-bg-secondary rounded-lg">
                                    <span className="text-xs text-text-secondary">Active / Pending</span>
                                    <span className="text-lg font-semibold text-status-warning">
                                        {loan.customer_loan_stats.active}
                                    </span>
                                </div>
                            </div>
                        </Card>
                    ) : undefined
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
                    <p className="text-xs text-status-danger mt-2">Failed to submit decision. Please try again.</p>
                )}
            </Modal>
        </>
    );
}
