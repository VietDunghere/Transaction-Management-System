import { useParams, useNavigate } from '@tanstack/react-router';
import { useTransaction, useTransactionStates } from '~/hooks/useTransactions';
import { useAuthStore } from '~/stores/useAuthStore';
import type { TransactionStatus } from '~/types/api';
import { PageHeader } from '~/components/templates/PageHeader/PageHeader';
import { DetailPageTemplate } from '~/components/templates/DetailPageTemplate/DetailPageTemplate';
import { Card } from '~/components/ui/Card/Card';
import { KeyValueRow } from '~/components/ui/KeyValueRow/KeyValueRow';
import { Badge } from '~/components/ui/Badge/Badge';
import { SectionHeader } from '~/components/ui/SectionHeader/SectionHeader';
import { TimelineItem } from '~/components/ui/TimelineItem/TimelineItem';
import { Button } from '~/components/ui/Button/Button';
import { LoadingSkeleton } from '~/components/ui/LoadingSkeleton/LoadingSkeleton';
import { ErrorState } from '~/components/ui/ErrorState/ErrorState';

const statusVariant: Record<TransactionStatus, 'success' | 'danger' | 'warning' | 'info'> = {
    APPROVED: 'success',
    REJECTED: 'danger',
    MANUAL_REVIEW: 'warning',
    PENDING: 'info',
};

const timelineVariant: Record<string, 'success' | 'danger' | 'warning' | 'default'> = {
    APPROVED: 'success',
    REJECTED: 'danger',
    MANUAL_REVIEW: 'warning',
};

export function TransactionDetailPage() {
    const { txnId } = useParams({ strict: false }) as { txnId: string };
    const navigate = useNavigate();
    const role = useAuthStore((s) => s.user?.role);
    const canViewHistory = role === 'ANALYST' || role === 'MANAGER';
    const { data: txn, isLoading, isError, refetch } = useTransaction(txnId);
    const { data: states } = useTransactionStates(canViewHistory ? txnId : '');

    if (isLoading) return <LoadingSkeleton variant="card" />;
    if (isError || !txn) return <ErrorState onRetry={refetch} />;

    return (
        <DetailPageTemplate
            header={
                <PageHeader
                    title="Transaction Detail"
                    subtitle={`Created ${new Date(txn.created_at).toLocaleString()}`}
                    actions={
                        <Button variant="ghost" onClick={() => navigate({ to: '/transactions' })}>
                            Back to List
                        </Button>
                    }
                />
            }
            statBar={
                <>
                    <div className="flex flex-col gap-2 rounded-xl bg-accent-purple p-6">
                        <span className="text-sm text-text-on-accent">Amount</span>
                        <span className="text-2xl font-semibold leading-8 text-text-on-accent">
                            {txn.amount.toLocaleString()} {txn.currency_code}
                        </span>
                    </div>
                    <div className="flex flex-col gap-2 rounded-xl bg-accent-blue p-6">
                        <span className="text-sm text-text-on-accent">Fraud Score</span>
                        <span className="text-2xl font-semibold leading-8 text-text-on-accent">
                            {(txn.fraud_score * 100).toFixed(1)}%
                        </span>
                    </div>
                    <div className="flex flex-col items-start gap-2 rounded-xl bg-accent-purple p-6">
                        <span className="text-sm text-text-on-accent">Status</span>
                        <Badge variant={statusVariant[txn.status]}>{txn.status}</Badge>
                    </div>
                    <div className="flex flex-col gap-2 rounded-xl bg-accent-blue p-6">
                        <span className="text-sm text-text-on-accent">Reason</span>
                        <span className="text-base font-semibold text-text-on-accent">{txn.reason_code ?? '-'}</span>
                    </div>
                </>
            }
            main={
                <Card>
                    <SectionHeader title="Transaction Details" />
                    <div className="flex flex-col gap-1 mt-4">
                        <KeyValueRow
                            label="Transaction ID"
                            value={<span className="font-mono text-xs">{txn.txn_id}</span>}
                        />
                        <KeyValueRow
                            label="Customer"
                            value={txn.customer_name ?? <span className="font-mono text-xs">{txn.customer_id}</span>}
                        />
                        <KeyValueRow
                            label="Merchant"
                            value={txn.merchant_name ?? <span className="font-mono text-xs">{txn.merchant_id}</span>}
                        />
                        <KeyValueRow label="Card Number" value={txn.card_number_masked} />
                        <KeyValueRow label="Amount" value={`${txn.amount.toLocaleString()} ${txn.currency_code}`} />
                        <KeyValueRow
                            label="Status"
                            value={<Badge variant={statusVariant[txn.status]}>{txn.status}</Badge>}
                        />
                        <KeyValueRow label="Fraud Score" value={`${(txn.fraud_score * 100).toFixed(1)}%`} />
                        <KeyValueRow label="Reason Code" value={txn.reason_code ?? '-'} />
                        <KeyValueRow label="Source IP" value={txn.source_ip} />
                        <KeyValueRow label="Transaction Time" value={new Date(txn.txn_time).toLocaleString()} />
                        <KeyValueRow label="Created At" value={new Date(txn.created_at).toLocaleString()} />
                        <KeyValueRow
                            label="Updated At"
                            value={txn.updated_at ? new Date(txn.updated_at).toLocaleString() : '-'}
                        />
                    </div>
                </Card>
            }
            fullWidth={
                states && states.length > 0 ? (
                    <Card>
                        <SectionHeader title="State History" />
                        <div className="flex flex-col gap-0 mt-4">
                            {states.map((entry) => (
                                <TimelineItem
                                    key={entry.state_hist_id}
                                    title={entry.new_status}
                                    description={entry.old_status ? `From ${entry.old_status}` : 'Initial state'}
                                    timestamp={new Date(entry.changed_at).toLocaleString()}
                                    variant={timelineVariant[entry.new_status] ?? 'default'}
                                />
                            ))}
                        </div>
                    </Card>
                ) : undefined
            }
        />
    );
}
