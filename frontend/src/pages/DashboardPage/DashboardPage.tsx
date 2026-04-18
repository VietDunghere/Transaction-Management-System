import { useDashboardSummary, useFraudTrend } from '~/hooks/useDashboard';
import { PageHeader } from '~/components/templates/PageHeader/PageHeader';
import { DashboardTemplate } from '~/components/templates/DashboardTemplate/DashboardTemplate';
import { StatCard } from '~/components/ui/StatCard/StatCard';
import { Card } from '~/components/ui/Card/Card';
import { SectionHeader } from '~/components/ui/SectionHeader/SectionHeader';
import { TableShell } from '~/components/ui/TableShell/TableShell';
import { LoadingSkeleton } from '~/components/ui/LoadingSkeleton/LoadingSkeleton';
import { ErrorState } from '~/components/ui/ErrorState/ErrorState';

export function DashboardPage() {
    const {
        data: summary,
        isLoading: summaryLoading,
        isError: summaryError,
        refetch: refetchSummary,
    } = useDashboardSummary();
    const { data: trend, isLoading: trendLoading } = useFraudTrend(30);

    if (summaryLoading) return <LoadingSkeleton variant="card" />;
    if (summaryError || !summary) return <ErrorState onRetry={refetchSummary} />;

    const { transactions, fraud, cases, loans } = summary;
    const rejectionPercent = (fraud.rejection_rate * 100).toFixed(2);

    return (
        <DashboardTemplate
            header={<PageHeader title="Dashboard" subtitle="System overview and fraud monitoring" />}
            kpiRow={
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <StatCard label="Transactions" value={transactions.total.toLocaleString()} accent="purple" />
                    <StatCard label="Today" value={transactions.today.toLocaleString()} accent="blue" />
                    <StatCard
                        label="Rejected"
                        value={`${rejectionPercent}%`}
                        changeType={parseFloat(rejectionPercent) > 5 ? 'negative' : 'positive'}
                        accent="purple"
                    />
                    <StatCard label="Open Cases" value={cases.total_open} accent="blue" />
                </div>
            }
            chartRow={
                <Card>
                    <SectionHeader title="Fraud Trend (Last 30 Days)" />
                    {trendLoading ? (
                        <LoadingSkeleton variant="chart" />
                    ) : trend && trend.data.length > 0 ? (
                        <div className="mt-4 overflow-x-auto">
                            <TableShell
                                columns={[
                                    { key: 'date', label: 'Date' },
                                    { key: 'total_txn', label: 'Total', align: 'right' },
                                    { key: 'approved', label: 'Approved', align: 'right' },
                                    { key: 'rejected', label: 'Rejected', align: 'right' },
                                    { key: 'manual_review', label: 'Review', align: 'right' },
                                    { key: 'fraud_rate', label: 'Fraud %', align: 'right' },
                                ]}
                                data={trend.data.slice(0, 10).map((d) => ({
                                    date: <span className="text-xs">{d.period_label}</span>,
                                    total_txn: <span className="text-sm">{d.total_txn}</span>,
                                    approved: (
                                        <span className="text-sm text-status-success">{d.approved}</span>
                                    ),
                                    rejected: (
                                        <span className="text-sm text-status-danger">{d.rejected}</span>
                                    ),
                                    manual_review: (
                                        <span className="text-sm text-status-warning">
                                            {d.manual_review}
                                        </span>
                                    ),
                                    fraud_rate: <span className="text-sm">{(d.fraud_rate * 100).toFixed(2)}%</span>,
                                }))}
                            />
                        </div>
                    ) : (
                        <p className="text-sm text-text-secondary mt-4">No trend data available.</p>
                    )}
                </Card>
            }
            secondaryCards={
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Card>
                        <SectionHeader title="Transactions by Status" />
                        <div className="flex flex-col gap-2 mt-4">
                            {[
                                { label: 'Approved', value: transactions.approved },
                                { label: 'Rejected', value: transactions.rejected },
                                { label: 'Manual Review', value: transactions.manual_review },
                                { label: 'Pending', value: transactions.pending },
                            ].map((item) => (
                                <div key={item.label} className="flex items-center justify-between py-1">
                                    <span className="text-sm text-text-secondary">{item.label}</span>
                                    <span className="text-sm font-medium">{item.value.toLocaleString()}</span>
                                </div>
                            ))}
                        </div>
                    </Card>
                    <Card>
                        <SectionHeader title="Loans & Cases" />
                        <div className="flex flex-col gap-2 mt-4">
                            {[
                                { label: 'Loans Pending', value: loans.total_pending },
                                { label: 'Loans Approved', value: loans.total_approved },
                                { label: 'Loans Rejected', value: loans.total_rejected },
                            ].map((item) => (
                                <div key={item.label} className="flex items-center justify-between py-1">
                                    <span className="text-sm text-text-secondary">{item.label}</span>
                                    <span className="text-sm font-medium">{item.value.toLocaleString()}</span>
                                </div>
                            ))}
                            <div className="flex items-center justify-between py-1 border-t border-border-default">
                                <span className="text-sm text-text-secondary">Cases Assigned</span>
                                <span className="text-sm font-medium">{cases.total_assigned}</span>
                            </div>
                        </div>
                    </Card>
                </div>
            }
        />
    );
}
