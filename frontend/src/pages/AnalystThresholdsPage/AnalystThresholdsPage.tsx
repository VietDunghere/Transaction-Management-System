import { useState } from 'react';
import { useThresholds, useUpdateThresholds } from '~/hooks/useAnalyst';
import { useAuthStore } from '~/stores/useAuthStore';
import { PageHeader } from '~/components/templates/PageHeader/PageHeader';
import { Card } from '~/components/ui/Card/Card';
import { SectionHeader } from '~/components/ui/SectionHeader/SectionHeader';
import { KeyValueRow } from '~/components/ui/KeyValueRow/KeyValueRow';
import { Button } from '~/components/ui/Button/Button';
import { Modal } from '~/components/ui/Modal/Modal';
import { Input } from '~/components/ui/Input/Input';
import { Select } from '~/components/ui/Select/Select';
import { LoadingSkeleton } from '~/components/ui/LoadingSkeleton/LoadingSkeleton';
import { ErrorState } from '~/components/ui/ErrorState/ErrorState';
import type { ThresholdItem } from '~/types/api';

const PARAM_LABELS: Record<string, string> = {
    reject_threshold: 'Reject Threshold',
    review_threshold: 'Review Threshold',
    high_risk_threshold: 'High Risk Threshold',
    medium_risk_threshold: 'Medium Risk Threshold',
};

const FRAUD_PARAMS = [
    { value: 'reject_threshold', label: 'Reject Threshold' },
    { value: 'review_threshold', label: 'Review Threshold' },
];

const LOAN_PARAMS = [
    { value: 'high_risk_threshold', label: 'High Risk Threshold' },
    { value: 'medium_risk_threshold', label: 'Medium Risk Threshold' },
];

export function AnalystThresholdsPage() {
    const role = useAuthStore((s) => s.user?.role);
    const canEdit = role === 'ANALYST';
    const { data, isLoading, isError, refetch } = useThresholds();
    const updateThresholds = useUpdateThresholds();

    const [modal, setModal] = useState(false);
    const [modelName, setModelName] = useState<'fraud' | 'loan'>('fraud');
    const [paramName, setParamName] = useState('reject_threshold');
    const [paramValue, setParamValue] = useState('');

    const paramOptions = modelName === 'fraud' ? FRAUD_PARAMS : LOAN_PARAMS;

    function renderThresholdRows(items: ThresholdItem[], model: 'fraud' | 'loan') {
        if (items.length === 0) {
            return (
                <p className="text-sm text-text-secondary">
                    Threshold data is unavailable. Please refresh or contact admin.
                </p>
            );
        }

        return items.map((item) => (
            <KeyValueRow
                key={item.param_name}
                label={PARAM_LABELS[item.param_name] ?? item.param_name}
                value={
                    <div className="flex items-center gap-4">
                        <span className="font-mono text-sm font-semibold">{item.param_value.toFixed(2)}</span>
                        <span className="text-xs text-text-secondary">
                            v{item.version} · {item.updated_by ?? '—'} · {new Date(item.updated_at).toLocaleDateString()}
                        </span>
                        {canEdit && (
                            <Button size="sm" variant="secondary" onClick={() => openModal(model, item)}>
                                Edit
                            </Button>
                        )}
                    </div>
                }
            />
        ));
    }

    function handleSubmit() {
        const val = parseFloat(paramValue);
        if (isNaN(val) || val <= 0 || val >= 1) return;
        updateThresholds.mutate(
            { updates: [{ model_name: modelName, param_name: paramName, param_value: val }] },
            { onSuccess: () => setModal(false) },
        );
    }

    function openModal(model: 'fraud' | 'loan', item: ThresholdItem) {
        setModelName(model);
        setParamName(item.param_name);
        setParamValue(String(item.param_value));
        setModal(true);
    }

    if (isLoading) return <LoadingSkeleton variant="card" />;
    if (isError || !data) return <ErrorState onRetry={refetch} />;

    return (
        <>
            <div className="flex flex-col gap-6">
                <PageHeader
                    title="Model Thresholds"
                    subtitle="View and update classification thresholds for Fraud and Loan models"
                />

                <Card>
                    <SectionHeader title="Fraud Detection Model" />
                    <div className="flex flex-col gap-1 mt-4">
                        {renderThresholdRows(data.fraud, 'fraud')}
                    </div>
                </Card>

                <Card>
                    <SectionHeader title="Loan PD Score Model" />
                    <div className="flex flex-col gap-1 mt-4">
                        {renderThresholdRows(data.loan, 'loan')}
                    </div>
                </Card>
            </div>

            <Modal
                isOpen={modal}
                onClose={() => setModal(false)}
                title="Update Threshold"
                footer={
                    <div className="flex justify-end gap-2">
                        <Button variant="ghost" onClick={() => setModal(false)}>Cancel</Button>
                        <Button onClick={handleSubmit} loading={updateThresholds.isPending}>Save</Button>
                    </div>
                }
            >
                <div className="flex flex-col gap-4">
                    <Select
                        label="Model"
                        options={[{ label: 'Fraud Detection', value: 'fraud' }, { label: 'Loan PD Score', value: 'loan' }]}
                        value={modelName}
                        onChange={(e) => {
                            const m = e.target.value as 'fraud' | 'loan';
                            setModelName(m);
                            setParamName(m === 'fraud' ? 'reject_threshold' : 'high_risk_threshold');
                        }}
                    />
                    <Select
                        label="Parameter"
                        options={paramOptions}
                        value={paramName}
                        onChange={(e) => setParamName(e.target.value)}
                    />
                    <Input
                        label="New Value (0.0 – 1.0)"
                        type="number"
                        step="0.01"
                        min="0.01"
                        max="0.99"
                        value={paramValue}
                        onChange={(e) => setParamValue(e.target.value)}
                    />
                    {updateThresholds.isError && (
                        <p className="text-xs text-status-danger">Failed to update. Please try again.</p>
                    )}
                </div>
            </Modal>
        </>
    );
}
