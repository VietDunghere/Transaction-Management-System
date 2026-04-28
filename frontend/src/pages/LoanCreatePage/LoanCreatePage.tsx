import { useState, useCallback } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate } from '@tanstack/react-router';
import { useCreateLoan } from '~/hooks/useLoans';
import { useSearchCustomers } from '~/hooks/useLookup';
import { PageHeader } from '~/components/templates/PageHeader/PageHeader';
import { FormPageTemplate } from '~/components/templates/FormPageTemplate/FormPageTemplate';
import { Card } from '~/components/ui/Card/Card';
import { Input } from '~/components/ui/Input/Input';
import { Select } from '~/components/ui/Select/Select';
import { Button } from '~/components/ui/Button/Button';
import { Combobox } from '~/components/ui/Combobox/Combobox';
import type { ComboboxOption } from '~/components/ui/Combobox/Combobox';

const createLoanSchema = z.object({
    customer_id: z.string().min(1, 'Please select a customer'),
    principal_amount: z
        .string()
        .min(1, 'Amount is required')
        .refine((v) => Number(v) > 0, 'Must be greater than 0'),
    currency_code: z.string().min(1, 'Currency is required'),
    interest_rate: z
        .string()
        .min(1, 'Interest rate is required')
        .refine((v) => Number(v) > 0 && Number(v) <= 100, '0-100%'),
    term_months: z
        .string()
        .min(1, 'Term is required')
        .refine((v) => Number(v) >= 1 && Number(v) <= 360, '1-360 months'),
    purpose: z.string().min(1, 'Please select a purpose'),
});

type CreateLoanForm = z.infer<typeof createLoanSchema>;

const currencyOptions = [
    { label: 'VND', value: 'VND' },
    { label: 'USD', value: 'USD' },
];

const purposeOptions = [
    { label: 'Personal', value: 'PERSONAL' },
    { label: 'Education', value: 'EDUCATION' },
    { label: 'Medical', value: 'MEDICAL' },
    { label: 'Venture', value: 'VENTURE' },
    { label: 'Home Improvement', value: 'HOMEIMPROVEMENT' },
    { label: 'Debt Consolidation', value: 'DEBTCONSOLIDATION' },
];

export function LoanCreatePage() {
    const navigate = useNavigate();
    const createLoan = useCreateLoan();

    // Combobox search state
    const [customerQuery, setCustomerQuery] = useState('');
    const [customerDisplay, setCustomerDisplay] = useState('');

    const { data: customers = [], isLoading: customersLoading } = useSearchCustomers(customerQuery);

    const {
        register,
        handleSubmit,
        setValue,
        watch,
        formState: { errors },
    } = useForm<CreateLoanForm>({
        resolver: zodResolver(createLoanSchema),
        defaultValues: {
            currency_code: 'VND',
        },
    });

    const customerId = watch('customer_id');

    const customerOptions: ComboboxOption[] = customers.map((c) => ({
        value: c.customer_id,
        label: `${c.full_name} (${c.customer_code})`,
    }));

    const handleCustomerSearch = useCallback((q: string) => setCustomerQuery(q), []);

    const handleCustomerSelect = useCallback(
        (value: string, label: string) => {
            setValue('customer_id', value, { shouldValidate: true });
            setCustomerDisplay(label);
        },
        [setValue],
    );

    const onSubmit = (data: CreateLoanForm) => {
        createLoan.mutate({
            customer_id: data.customer_id,
            principal_amount: Number(data.principal_amount),
            currency_code: data.currency_code,
            interest_rate: Number(data.interest_rate),
            term_months: Number(data.term_months),
            purpose: data.purpose,
        });
    };

    return (
        <FormPageTemplate
            header={
                <PageHeader
                    title="Create Loan"
                    subtitle="Submit a new loan application"
                    actions={
                        <Button variant="ghost" onClick={() => navigate({ to: '/loans' })}>
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
                            <Input
                                label="Principal Amount"
                                type="number"
                                error={errors.principal_amount?.message}
                                {...register('principal_amount')}
                            />
                            <Select
                                label="Currency"
                                options={currencyOptions}
                                error={errors.currency_code?.message}
                                {...register('currency_code')}
                            />
                            <Input
                                label="Interest Rate (%)"
                                type="number"
                                step="0.01"
                                error={errors.interest_rate?.message}
                                {...register('interest_rate')}
                            />
                            <Input
                                label="Term (months)"
                                type="number"
                                error={errors.term_months?.message}
                                {...register('term_months')}
                            />
                            <Select
                                label="Purpose"
                                placeholder="Select a purpose"
                                options={purposeOptions}
                                error={errors.purpose?.message}
                                {...register('purpose')}
                            />
                        </div>

                        {createLoan.isSuccess && (
                            <div className="flex items-center gap-2 p-3 rounded-sm bg-secondary">
                                <span className="text-sm text-status-success font-medium">
                                    Loan submitted successfully
                                </span>
                                <Button
                                    variant="ghost"
                                    className="ml-auto text-xs"
                                    onClick={() =>
                                        navigate({
                                            to: '/loans/$loanId',
                                            params: { loanId: createLoan.data.loan_id },
                                        })
                                    }
                                >
                                    View Loan →
                                </Button>
                            </div>
                        )}

                        {createLoan.isError && (
                            <p className="text-xs text-status-danger">Failed to create loan. Please try again.</p>
                        )}

                        <div className="flex justify-end">
                            <Button type="submit" loading={createLoan.isPending}>
                                Submit Loan
                            </Button>
                        </div>
                    </form>
                </Card>
            }
        />
    );
}
