import { useState, useCallback } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate } from '@tanstack/react-router';
import { useSubmitTransaction } from '~/hooks/useTransactions';
import { useSearchCustomers, useSearchMerchants, useChannels } from '~/hooks/useLookup';
import { PageHeader } from '~/components/templates/PageHeader/PageHeader';
import { FormPageTemplate } from '~/components/templates/FormPageTemplate/FormPageTemplate';
import { Card } from '~/components/ui/Card/Card';
import { Input } from '~/components/ui/Input/Input';
import { Select } from '~/components/ui/Select/Select';
import { Button } from '~/components/ui/Button/Button';
import { Badge } from '~/components/ui/Badge/Badge';
import { Combobox } from '~/components/ui/Combobox/Combobox';
import type { ComboboxOption } from '~/components/ui/Combobox/Combobox';

const submitSchema = z.object({
    customer_id: z.string().min(1, 'Please select a customer'),
    merchant_id: z.string().min(1, 'Please select a merchant'),
    channel_id: z.string().min(1, 'Please select a channel'),
    card_number: z
        .string()
        .transform((v) => v.replace(/[\s-]/g, ''))
        .pipe(z.string().min(13, 'Card number must be 13-19 digits').max(19).regex(/^\d+$/, 'Digits only')),
    amount: z.string().min(1, 'Amount is required'),
    txn_time: z.string().min(1, 'Transaction time is required'),
});

type SubmitForm = z.infer<typeof submitSchema>;



export function TransactionSubmitPage() {
    const navigate = useNavigate();
    const submitTxn = useSubmitTransaction();

    // Combobox search state
    const [customerQuery, setCustomerQuery] = useState('');
    const [merchantQuery, setMerchantQuery] = useState('');

    // Display values for comboboxes
    const [customerDisplay, setCustomerDisplay] = useState('');
    const [merchantDisplay, setMerchantDisplay] = useState('');

    // Lookup hooks
    const { data: customers = [], isLoading: customersLoading } = useSearchCustomers(customerQuery);
    const { data: merchants = [], isLoading: merchantsLoading } = useSearchMerchants(merchantQuery);
    const { data: channels = [] } = useChannels();

    const {
        register,
        handleSubmit,
        setValue,
        watch,
        formState: { errors },
    } = useForm<SubmitForm>({
        resolver: zodResolver(submitSchema),
        defaultValues: {
            txn_time: new Date().toISOString().slice(0, 16),
        },
    });

    const customerId = watch('customer_id');
    const merchantId = watch('merchant_id');

    // Map API data to combobox options
    const customerOptions: ComboboxOption[] = customers.map((c) => ({
        value: c.customer_id,
        label: `${c.full_name} (${c.customer_code})`,
    }));

    const merchantOptions: ComboboxOption[] = merchants.map((m) => ({
        value: m.merchant_id,
        label: `${m.merchant_name} (${m.merchant_code})`,
        sublabel: m.merchant_category ?? undefined,
    }));

    const channelOptions = channels.map((ch) => ({
        label: ch.channel_name,
        value: String(ch.channel_id),
    }));

    const handleCustomerSearch = useCallback((q: string) => setCustomerQuery(q), []);
    const handleMerchantSearch = useCallback((q: string) => setMerchantQuery(q), []);

    const handleCustomerSelect = useCallback(
        (value: string, label: string) => {
            setValue('customer_id', value, { shouldValidate: true });
            setCustomerDisplay(label);
        },
        [setValue],
    );

    const handleMerchantSelect = useCallback(
        (value: string, label: string) => {
            setValue('merchant_id', value, { shouldValidate: true });
            setMerchantDisplay(label);
        },
        [setValue],
    );

    const onSubmit = (data: SubmitForm) => {
        submitTxn.mutate({
            customer_id: data.customer_id,
            merchant_id: data.merchant_id,
            channel_id: Number(data.channel_id),
            card_number: data.card_number.replace(/[\s-]/g, ''),
            amount: Number(data.amount),
            txn_time: new Date(data.txn_time).toISOString(),
        });
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
                            <Combobox
                                label="Customer"
                                placeholder="Search by name or code..."
                                error={errors.customer_id?.message}
                                value={customerId ?? ''}
                                displayValue={customerDisplay}
                                options={customerOptions}
                                onSearch={handleCustomerSearch}
                                onSelect={handleCustomerSelect}
                                loading={customersLoading}
                            />
                            <Combobox
                                label="Merchant"
                                placeholder="Search by name or code..."
                                error={errors.merchant_id?.message}
                                value={merchantId ?? ''}
                                displayValue={merchantDisplay}
                                options={merchantOptions}
                                onSearch={handleMerchantSearch}
                                onSelect={handleMerchantSelect}
                                loading={merchantsLoading}
                            />
                            <Select
                                label="Channel"
                                placeholder="Select a channel"
                                options={channelOptions}
                                error={errors.channel_id?.message}
                                {...register('channel_id')}
                            />
                            <Input
                                label="Card Number"
                                placeholder="4111 1111 1111 1111"
                                error={errors.card_number?.message}
                                {...register('card_number')}
                            />
                            <Input
                                label="Amount"
                                type="number"
                                error={errors.amount?.message}
                                {...register('amount')}
                            />
                            <Input
                                label="Transaction Time"
                                type="datetime-local"
                                error={errors.txn_time?.message}
                                {...register('txn_time')}
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
                                <span className="text-xs text-text-secondary">
                                    Fraud Score: {(submitTxn.data.fraud_score * 100).toFixed(1)}%
                                </span>
                                <Button
                                    variant="ghost"
                                    className="ml-auto text-xs"
                                    onClick={() =>
                                        navigate({
                                            to: '/transactions/$txnId',
                                            params: { txnId: submitTxn.data.txn_id },
                                        })
                                    }
                                >
                                    View Transaction →
                                </Button>
                            </div>
                        )}

                        {submitTxn.isError && (
                            <p className="text-xs text-status-danger">
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
        />
    );
}
