import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate } from '@tanstack/react-router';
import { useSubmitTransaction } from '~/hooks/useTransactions';
import { PageHeader } from '~/components/templates/PageHeader/PageHeader';
import { FormPageTemplate } from '~/components/templates/FormPageTemplate/FormPageTemplate';
import { Card } from '~/components/ui/Card/Card';
import { Input } from '~/components/ui/Input/Input';
import { Select } from '~/components/ui/Select/Select';
import { Button } from '~/components/ui/Button/Button';
import { Badge } from '~/components/ui/Badge/Badge';

const submitSchema = z.object({
    customer_id: z.string().min(1, 'Customer ID is required'),
    merchant_id: z.string().min(1, 'Merchant ID is required'),
    channel_id: z.string().min(1, 'Channel ID is required'),
    card_number_masked: z.string().min(1, 'Card number is required'),
    amount: z.string().min(1, 'Amount is required'),
    currency_code: z.string().min(1, 'Currency is required'),
    txn_time: z.string().min(1, 'Transaction time is required'),
    source_ip: z.string().min(1, 'Source IP is required'),
});

type SubmitForm = z.infer<typeof submitSchema>;

const currencyOptions = [
    { label: 'VND', value: 'VND' },
    { label: 'USD', value: 'USD' },
];

export function TransactionSubmitPage() {
    const navigate = useNavigate();
    const submitTxn = useSubmitTransaction();

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<SubmitForm>({
        resolver: zodResolver(submitSchema),
        defaultValues: {
            currency_code: 'VND',
            txn_time: new Date().toISOString().slice(0, 16),
        },
    });

    const onSubmit = (data: SubmitForm) => {
        submitTxn.mutate(
            {
                ...data,
                channel_id: Number(data.channel_id),
                amount: Number(data.amount),
                txn_time: new Date(data.txn_time).toISOString(),
            },
            {
                onSuccess: (res) => {
                    navigate({ to: '/transactions/$txnId', params: { txnId: res.txn_id } });
                },
            },
        );
    };

    return (
        <FormPageTemplate
            header={
                <PageHeader
                    title="Submit Transaction"
                    subtitle="Submit a new transaction for fraud scoring"
                    actions={
                        <Button variant="ghost" onClick={() => navigate({ to: '/transactions' })}>
                            Cancel
                        </Button>
                    }
                />
            }
            form={
                <Card>
                    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <Input
                                label="Customer ID"
                                error={errors.customer_id?.message}
                                {...register('customer_id')}
                            />
                            <Input
                                label="Merchant ID"
                                error={errors.merchant_id?.message}
                                {...register('merchant_id')}
                            />
                            <Input
                                label="Channel ID"
                                type="number"
                                error={errors.channel_id?.message}
                                {...register('channel_id')}
                            />
                            <Input
                                label="Card Number (masked)"
                                placeholder="4111********1111"
                                error={errors.card_number_masked?.message}
                                {...register('card_number_masked')}
                            />
                            <Input
                                label="Amount"
                                type="number"
                                error={errors.amount?.message}
                                {...register('amount')}
                            />
                            <Select
                                label="Currency"
                                options={currencyOptions}
                                error={errors.currency_code?.message}
                                {...register('currency_code')}
                            />
                            <Input
                                label="Transaction Time"
                                type="datetime-local"
                                error={errors.txn_time?.message}
                                {...register('txn_time')}
                            />
                            <Input
                                label="Source IP"
                                placeholder="192.168.1.1"
                                error={errors.source_ip?.message}
                                {...register('source_ip')}
                            />
                        </div>

                        {submitTxn.isSuccess && (
                            <div className="flex items-center gap-2 p-3 rounded-sm bg-secondary">
                                <span className="text-sm">Result:</span>
                                <Badge
                                    variant={
                                        submitTxn.data.status === 'APPROVED'
                                            ? 'success'
                                            : submitTxn.data.status === 'REJECTED'
                                              ? 'danger'
                                              : 'warning'
                                    }
                                >
                                    {submitTxn.data.status}
                                </Badge>
                                <span className="text-xs text-[var(--color-text-secondary)]">
                                    Fraud Score: {(submitTxn.data.fraud_score * 100).toFixed(1)}%
                                </span>
                            </div>
                        )}

                        {submitTxn.isError && (
                            <p className="text-xs text-[var(--color-status-danger)]">
                                Failed to submit transaction. Please try again.
                            </p>
                        )}

                        <div className="flex justify-end">
                            <Button type="submit" loading={submitTxn.isPending}>
                                Submit for Scoring
                            </Button>
                        </div>
                    </form>
                </Card>
            }
            footer={<div />}
        />
    );
}
