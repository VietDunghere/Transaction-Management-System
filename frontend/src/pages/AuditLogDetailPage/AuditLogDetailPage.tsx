import { useParams, useNavigate } from '@tanstack/react-router';
import { useAuditLog } from '~/hooks/useAuditLogs';
import type { AuditEntityType } from '~/types/api';
import { PageHeader } from '~/components/templates/PageHeader/PageHeader';
import { DetailPageTemplate } from '~/components/templates/DetailPageTemplate/DetailPageTemplate';
import { Card } from '~/components/ui/Card/Card';
import { KeyValueRow } from '~/components/ui/KeyValueRow/KeyValueRow';
import { Badge } from '~/components/ui/Badge/Badge';
import { SectionHeader } from '~/components/ui/SectionHeader/SectionHeader';
import { Button } from '~/components/ui/Button/Button';
import { LoadingSkeleton } from '~/components/ui/LoadingSkeleton/LoadingSkeleton';
import { ErrorState } from '~/components/ui/ErrorState/ErrorState';

const entityVariant: Record<AuditEntityType, 'info' | 'warning' | 'success' | 'danger'> = {
    Transaction: 'info',
    User: 'success',
    ReviewCase: 'warning',
    Loan: 'danger',
};

export function AuditLogDetailPage() {
    const { logId } = useParams({ strict: false }) as { logId: string };
    const navigate = useNavigate();
    const { data: log, isLoading, isError, refetch } = useAuditLog(logId);

    if (isLoading) return <LoadingSkeleton variant="card" />;
    if (isError || !log) return <ErrorState onRetry={refetch} />;

    const detailJson =
        typeof log.detail_json === 'string' ? log.detail_json : JSON.stringify(log.detail_json, null, 2);

    return (
        <DetailPageTemplate
            header={
                <PageHeader
                    title={`Audit Log ${log.log_id.slice(0, 8)}...`}
                    subtitle={`${log.event_type} — ${new Date(log.event_ts).toLocaleString()}`}
                    actions={
                        <Button variant="ghost" onClick={() => navigate({ to: '/audit-logs' })}>
                            Back to List
                        </Button>
                    }
                />
            }
            info={
                <Card>
                    <SectionHeader title="Event Details" />
                    <div className="flex flex-col gap-1 mt-4">
                        <KeyValueRow
                            label="Log ID"
                            value={<span className="font-mono text-xs">{log.log_id}</span>}
                        />
                        <KeyValueRow label="Event Type" value={log.event_type} />
                        <KeyValueRow
                            label="Entity Type"
                            value={<Badge variant={entityVariant[log.entity_type]}>{log.entity_type}</Badge>}
                        />
                        <KeyValueRow
                            label="Entity ID"
                            value={<span className="font-mono text-xs">{log.entity_id}</span>}
                        />
                        <KeyValueRow label="Actor" value={log.actor_name} />
                        <KeyValueRow
                            label="Actor ID"
                            value={<span className="font-mono text-xs">{log.actor_user_id}</span>}
                        />
                        <KeyValueRow label="Timestamp" value={new Date(log.event_ts).toLocaleString()} />
                    </div>

                    <SectionHeader title="Detail JSON" className="mt-6" />
                    <pre className="mt-4 p-4 rounded-sm bg-secondary text-xs font-mono overflow-x-auto whitespace-pre-wrap break-all">
                        {detailJson}
                    </pre>
                </Card>
            }
        />
    );
}
