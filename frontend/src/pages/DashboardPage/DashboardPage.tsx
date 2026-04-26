import { useMemo } from 'react';
import ReactECharts from 'echarts-for-react';
import { useDashboardSummary, useFraudTrend } from '~/hooks/useDashboard';
import { PageHeader } from '~/components/templates/PageHeader/PageHeader';
import { DashboardTemplate } from '~/components/templates/DashboardTemplate/DashboardTemplate';
import { StatCard } from '~/components/ui/StatCard/StatCard';
import { Card } from '~/components/ui/Card/Card';
import { SectionHeader } from '~/components/ui/SectionHeader/SectionHeader';
import { LoadingSkeleton } from '~/components/ui/LoadingSkeleton/LoadingSkeleton';
import { ErrorState } from '~/components/ui/ErrorState/ErrorState';

interface TrendPoint {
    period_label: string;
    approved: number;
    rejected: number;
    manual_review: number;
}

function FraudTrendChart({ data }: { data: TrendPoint[] }) {
    const option = useMemo(
        () => ({
            tooltip: {
                trigger: 'axis' as const,
                axisPointer: { type: 'cross' as const },
            },
            legend: {
                data: ['Approved', 'Rejected', 'Manual Review'],
                bottom: 0,
                textStyle: { color: '#888' },
            },
            toolbox: {
                feature: {
                    saveAsImage: { title: 'Save' },
                },
            },
            grid: {
                left: 48,
                right: 24,
                top: 16,
                bottom: 80,
                containLabel: false,
            },
            dataZoom: [
                {
                    type: 'slider' as const,
                    start: 0,
                    end: 100,
                    bottom: 30,
                    height: 20,
                },
                { type: 'inside' as const },
            ],
            xAxis: {
                type: 'category' as const,
                data: data.map((d) => d.period_label),
                axisLabel: { fontSize: 11, color: '#888' },
            },
            yAxis: {
                type: 'value' as const,
                axisLabel: { fontSize: 11, color: '#888' },
                splitLine: { lineStyle: { color: 'rgba(128,128,128,0.15)' } },
            },
            series: [
                {
                    name: 'Approved',
                    type: 'line',
                    smooth: true,
                    symbol: 'circle',
                    symbolSize: 5,
                    areaStyle: { opacity: 0.15 },
                    itemStyle: { color: '#22c55e' },
                    data: data.map((d) => d.approved),
                },
                {
                    name: 'Rejected',
                    type: 'line',
                    smooth: true,
                    symbol: 'circle',
                    symbolSize: 5,
                    areaStyle: { opacity: 0.15 },
                    itemStyle: { color: '#ef4444' },
                    data: data.map((d) => d.rejected),
                },
                {
                    name: 'Manual Review',
                    type: 'line',
                    smooth: true,
                    symbol: 'circle',
                    symbolSize: 5,
                    areaStyle: { opacity: 0.15 },
                    itemStyle: { color: '#f59e0b' },
                    data: data.map((d) => d.manual_review),
                },
            ],
        }),
        [data],
    );

    return (
        <div className="mt-4">
            <ReactECharts option={option} style={{ height: 350 }} />
        </div>
    );
}

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
                        <FraudTrendChart data={trend.data} />
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
