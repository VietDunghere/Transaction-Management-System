import { useState } from 'react';
import { useFraudPerformance, useLoanPerformance } from '~/hooks/useAnalyst';
import { PageHeader } from '~/components/templates/PageHeader/PageHeader';
import { DashboardTemplate } from '~/components/templates/DashboardTemplate/DashboardTemplate';
import { Card } from '~/components/ui/Card/Card';
import { SectionHeader } from '~/components/ui/SectionHeader/SectionHeader';
import { StatCard } from '~/components/ui/StatCard/StatCard';
import { Select } from '~/components/ui/Select/Select';
import { KeyValueRow } from '~/components/ui/KeyValueRow/KeyValueRow';
import { Badge } from '~/components/ui/Badge/Badge';
import { LoadingSkeleton } from '~/components/ui/LoadingSkeleton/LoadingSkeleton';
import { ErrorState } from '~/components/ui/ErrorState/ErrorState';

const periodOptions = [
    { label: 'Last 7 days', value: '7' },
    { label: 'Last 30 days', value: '30' },
    { label: 'Last 90 days', value: '90' },
];

function pct(v: number) {
    return `${(v * 100).toFixed(1)}%`;
}

export function AnalystModelPerformancePage() {
    const [days, setDays] = useState(30);
    const [tab, setTab] = useState<'fraud' | 'loan'>('fraud');

    const fraud = useFraudPerformance(days);
    const loan = useLoanPerformance(days);

    const isLoading = tab === 'fraud' ? fraud.isLoading : loan.isLoading;
    const isError = tab === 'fraud' ? fraud.isError : loan.isError;
    const refetch = tab === 'fraud' ? fraud.refetch : loan.refetch;

    return (
        <DashboardTemplate
            header={
                <PageHeader
                    title="Model Performance"
                    subtitle="Evaluate fraud detection and loan PD score model effectiveness"
                    actions={
                        <div className="flex items-center gap-3">
                            <div className="flex rounded-lg border border-border-default overflow-hidden">
                                {(['fraud', 'loan'] as const).map((t) => (
                                    <button
                                        key={t}
                                        onClick={() => setTab(t)}
                                        className={`px-4 py-2 text-sm font-medium transition-colors duration-150 ${
                                            tab === t
                                                ? 'bg-text-primary text-bg-primary'
                                                : 'text-text-secondary hover:bg-subtle'
                                        }`}
                                    >
                                        {t === 'fraud' ? 'Fraud Model' : 'Loan Model'}
                                    </button>
                                ))}
                            </div>
                            <Select
                                options={periodOptions}
                                value={String(days)}
                                onChange={(e) => setDays(Number(e.target.value))}
                            />
                        </div>
                    }
                />
            }
            kpiRow={
                isLoading ? (
                    <LoadingSkeleton variant="card" />
                ) : isError ? (
                    <ErrorState onRetry={refetch} />
                ) : tab === 'fraud' && fraud.data ? (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <StatCard
                            label="Total Transactions"
                            value={fraud.data.score_distribution.total}
                            accent="purple"
                        />
                        <StatCard
                            label="Auto Approved"
                            value={pct(fraud.data.score_distribution.approved_rate)}
                            accent="blue"
                        />
                        <StatCard
                            label="Manual Review Rate"
                            value={pct(fraud.data.score_distribution.review_rate)}
                            accent="purple"
                        />
                        <StatCard
                            label="False Positive Rate"
                            value={pct(fraud.data.score_distribution.false_positive_rate)}
                            accent="blue"
                        />
                    </div>
                ) : loan.data ? (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <StatCard
                            label="Total Loans Scored"
                            value={loan.data.risk_distribution.total}
                            accent="purple"
                        />
                        <StatCard
                            label="Low Risk"
                            value={pct(loan.data.risk_distribution.low_risk_rate)}
                            accent="blue"
                        />
                        <StatCard
                            label="High Risk"
                            value={pct(loan.data.risk_distribution.high_risk_rate)}
                            accent="purple"
                        />
                        <StatCard label="Approved" value={loan.data.risk_distribution.approved_count} accent="blue" />
                    </div>
                ) : null
            }
            chartRow={
                !isLoading &&
                !isError && (
                    <Card>
                        <SectionHeader title="Current Thresholds" />
                        <div className="flex flex-col gap-1 mt-4">
                            {Object.entries(
                                tab === 'fraud'
                                    ? (fraud.data?.current_thresholds ?? {})
                                    : (loan.data?.current_thresholds ?? {}),
                            ).map(([key, val]) => (
                                <KeyValueRow
                                    key={key}
                                    label={key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
                                    value={<span className="font-mono text-sm">{val.toFixed(2)}</span>}
                                />
                            ))}
                        </div>
                    </Card>
                )
            }
            secondaryCards={
                !isLoading &&
                !isError && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {tab === 'fraud' && fraud.data && (
                            <>
                                <Card>
                                    <SectionHeader title="Score Distribution" />
                                    <div className="flex flex-col gap-1 mt-4">
                                        <KeyValueRow
                                            label="Approved"
                                            value={
                                                <div className="flex items-center gap-2">
                                                    <Badge variant="success">
                                                        {fraud.data.score_distribution.approved_count}
                                                    </Badge>
                                                    <span className="text-xs text-text-secondary">
                                                        {pct(fraud.data.score_distribution.approved_rate)}
                                                    </span>
                                                </div>
                                            }
                                        />
                                        <KeyValueRow
                                            label="Manual Review"
                                            value={
                                                <div className="flex items-center gap-2">
                                                    <Badge variant="warning">
                                                        {fraud.data.score_distribution.review_count}
                                                    </Badge>
                                                    <span className="text-xs text-text-secondary">
                                                        {pct(fraud.data.score_distribution.review_rate)}
                                                    </span>
                                                </div>
                                            }
                                        />
                                        <KeyValueRow
                                            label="Rejected"
                                            value={
                                                <div className="flex items-center gap-2">
                                                    <Badge variant="danger">
                                                        {fraud.data.score_distribution.rejected_count}
                                                    </Badge>
                                                    <span className="text-xs text-text-secondary">
                                                        {pct(fraud.data.score_distribution.rejected_rate)}
                                                    </span>
                                                </div>
                                            }
                                        />
                                    </div>
                                </Card>
                                <Card>
                                    <SectionHeader title="False Positives" />
                                    <div className="flex flex-col gap-1 mt-4">
                                        <KeyValueRow
                                            label="False Positive Count"
                                            value={
                                                <Badge variant="warning">
                                                    {fraud.data.score_distribution.false_positive_count}
                                                </Badge>
                                            }
                                        />
                                        <KeyValueRow
                                            label="False Positive Rate"
                                            value={
                                                <span className="font-mono text-sm">
                                                    {pct(fraud.data.score_distribution.false_positive_rate)}
                                                </span>
                                            }
                                        />
                                        <KeyValueRow
                                            label="Analysis Period"
                                            value={<span className="text-sm">{fraud.data.period_days} days</span>}
                                        />
                                    </div>
                                </Card>
                            </>
                        )}
                        {tab === 'loan' && loan.data && (
                            <>
                                <Card>
                                    <SectionHeader title="Risk Distribution" />
                                    <div className="flex flex-col gap-1 mt-4">
                                        <KeyValueRow
                                            label="Low Risk"
                                            value={
                                                <div className="flex items-center gap-2">
                                                    <Badge variant="success">
                                                        {loan.data.risk_distribution.low_risk_count}
                                                    </Badge>
                                                    <span className="text-xs text-text-secondary">
                                                        {pct(loan.data.risk_distribution.low_risk_rate)}
                                                    </span>
                                                </div>
                                            }
                                        />
                                        <KeyValueRow
                                            label="Medium Risk"
                                            value={
                                                <div className="flex items-center gap-2">
                                                    <Badge variant="warning">
                                                        {loan.data.risk_distribution.medium_risk_count}
                                                    </Badge>
                                                    <span className="text-xs text-text-secondary">
                                                        {pct(loan.data.risk_distribution.medium_risk_rate)}
                                                    </span>
                                                </div>
                                            }
                                        />
                                        <KeyValueRow
                                            label="High Risk"
                                            value={
                                                <div className="flex items-center gap-2">
                                                    <Badge variant="danger">
                                                        {loan.data.risk_distribution.high_risk_count}
                                                    </Badge>
                                                    <span className="text-xs text-text-secondary">
                                                        {pct(loan.data.risk_distribution.high_risk_rate)}
                                                    </span>
                                                </div>
                                            }
                                        />
                                    </div>
                                </Card>
                                <Card>
                                    <SectionHeader title="Loan Outcomes" />
                                    <div className="flex flex-col gap-1 mt-4">
                                        <KeyValueRow
                                            label="Approved"
                                            value={
                                                <Badge variant="success">
                                                    {loan.data.risk_distribution.approved_count}
                                                </Badge>
                                            }
                                        />
                                        <KeyValueRow
                                            label="Rejected"
                                            value={
                                                <Badge variant="danger">
                                                    {loan.data.risk_distribution.rejected_count}
                                                </Badge>
                                            }
                                        />
                                        <KeyValueRow
                                            label="Pending"
                                            value={
                                                <Badge variant="info">
                                                    {loan.data.risk_distribution.pending_count}
                                                </Badge>
                                            }
                                        />
                                    </div>
                                </Card>
                            </>
                        )}
                    </div>
                )
            }
        />
    );
}
