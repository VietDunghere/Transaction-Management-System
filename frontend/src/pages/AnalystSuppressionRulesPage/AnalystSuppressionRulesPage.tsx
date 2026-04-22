import { useState } from 'react';
import { useSuppressionRules, useCreateSuppressionRule, useDisableSuppressionRule } from '~/hooks/useAnalyst';
import { useAuthStore } from '~/stores/useAuthStore';
import { PageHeader } from '~/components/templates/PageHeader/PageHeader';
import { ListPageTemplate } from '~/components/templates/ListPageTemplate/ListPageTemplate';
import { TableShell } from '~/components/ui/TableShell/TableShell';
import { FilterBar } from '~/components/ui/FilterBar/FilterBar';
import { Select } from '~/components/ui/Select/Select';
import { Button } from '~/components/ui/Button/Button';
import { Badge } from '~/components/ui/Badge/Badge';
import { Modal } from '~/components/ui/Modal/Modal';
import { Input } from '~/components/ui/Input/Input';
import { Textarea } from '~/components/ui/Textarea/Textarea';
import { LoadingSkeleton } from '~/components/ui/LoadingSkeleton/LoadingSkeleton';
import { ErrorState } from '~/components/ui/ErrorState/ErrorState';
import { EmptyState } from '~/components/ui/EmptyState/EmptyState';
import type { SuppressionRuleCreateRequest } from '~/types/api';

const columns = [
    { key: 'rule_type', label: 'Type' },
    { key: 'entity_id', label: 'Entity ID' },
    { key: 'reason', label: 'Reason' },
    { key: 'expires_at', label: 'Expires' },
    { key: 'status', label: 'Status' },
    { key: 'created_at', label: 'Created' },
    { key: 'actions', label: '' },
];

const ruleTypeOptions = [
    { label: 'Merchant', value: 'MERCHANT' },
    { label: 'Customer', value: 'CUSTOMER' },
    { label: 'Card Hash', value: 'CARD_HASH' },
];

export function AnalystSuppressionRulesPage() {
    const role = useAuthStore((s) => s.user?.role);
    const canEdit = role === 'ANALYST' || role === 'ADMIN';

    const [showInactive, setShowInactive] = useState(false);
    const { data, isLoading, isError, refetch } = useSuppressionRules(showInactive);
    const createRule = useCreateSuppressionRule();
    const disableRule = useDisableSuppressionRule();

    const [createModal, setCreateModal] = useState(false);
    const [form, setForm] = useState<SuppressionRuleCreateRequest>({
        rule_type: 'MERCHANT',
        entity_id: '',
        reason: '',
        expires_at: undefined,
    });

    function handleCreate() {
        createRule.mutate(form, {
            onSuccess: () => {
                setCreateModal(false);
                setForm({ rule_type: 'MERCHANT', entity_id: '', reason: '' });
            },
        });
    }

    const rules = data ?? [];
    const rows = rules.map((rule) => ({
        rule_type: <Badge variant="info">{rule.rule_type}</Badge>,
        entity_id: <span className="font-mono text-xs">{rule.entity_id}</span>,
        reason: <span className="text-sm max-w-xs truncate block">{rule.reason}</span>,
        expires_at: (
            <span className="text-xs text-text-secondary">
                {rule.expires_at ? new Date(rule.expires_at).toLocaleDateString() : 'Never'}
            </span>
        ),
        status: <Badge variant={rule.is_active ? 'success' : 'muted'}>{rule.is_active ? 'Active' : 'Disabled'}</Badge>,
        created_at: (
            <span className="text-xs text-text-secondary">{new Date(rule.created_at).toLocaleDateString()}</span>
        ),
        actions:
            rule.is_active && canEdit ? (
                <Button
                    size="sm"
                    variant="ghost"
                    onClick={(e) => {
                        e.stopPropagation();
                        disableRule.mutate(rule.rule_id);
                    }}
                >
                    Disable
                </Button>
            ) : null,
    }));

    return (
        <>
            <ListPageTemplate
                header={
                    <PageHeader
                        title="Suppression Rules"
                        subtitle={`${rules.filter((r) => r.is_active).length} active rules`}
                        actions={canEdit ? <Button onClick={() => setCreateModal(true)}>New Rule</Button> : undefined}
                    />
                }
                filterBar={
                    <FilterBar>
                        <Select
                            options={[
                                { label: 'Active only', value: 'false' },
                                { label: 'Include inactive', value: 'true' },
                            ]}
                            value={showInactive ? 'true' : 'false'}
                            onChange={(e) => setShowInactive(e.target.value === 'true')}
                        />
                    </FilterBar>
                }
                table={
                    isLoading ? (
                        <LoadingSkeleton variant="table" rows={6} />
                    ) : isError ? (
                        <ErrorState onRetry={refetch} />
                    ) : rows.length === 0 ? (
                        <EmptyState
                            title="No suppression rules"
                            description="Create a rule to suppress flagged transactions."
                        />
                    ) : (
                        <TableShell columns={columns} data={rows} />
                    )
                }
            />

            <Modal
                isOpen={createModal}
                onClose={() => setCreateModal(false)}
                title="New Suppression Rule"
                footer={
                    <div className="flex justify-end gap-2">
                        <Button variant="ghost" onClick={() => setCreateModal(false)}>
                            Cancel
                        </Button>
                        <Button onClick={handleCreate} loading={createRule.isPending}>
                            Create
                        </Button>
                    </div>
                }
            >
                <div className="flex flex-col gap-4">
                    <Select
                        label="Rule Type"
                        options={ruleTypeOptions}
                        value={form.rule_type}
                        onChange={(e) => setForm((f) => ({ ...f, rule_type: e.target.value as any }))}
                    />
                    <Input
                        label="Entity ID"
                        placeholder="merchant ID, customer ID, or card hash"
                        value={form.entity_id}
                        onChange={(e) => setForm((f) => ({ ...f, entity_id: e.target.value }))}
                    />
                    <Textarea
                        label="Reason (min 5 chars)"
                        placeholder="Why is this entity being suppressed?"
                        value={form.reason}
                        onChange={(e) => setForm((f) => ({ ...f, reason: e.target.value }))}
                    />
                    <Input
                        label="Expires At (optional)"
                        type="datetime-local"
                        value={form.expires_at ?? ''}
                        onChange={(e) => setForm((f) => ({ ...f, expires_at: e.target.value || undefined }))}
                    />
                    {createRule.isError && (
                        <p className="text-xs text-status-danger">Failed to create rule. Please try again.</p>
                    )}
                </div>
            </Modal>
        </>
    );
}
