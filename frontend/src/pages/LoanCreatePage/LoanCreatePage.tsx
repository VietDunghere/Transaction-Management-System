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
    interest_rate: z
        .string()
        .min(1, 'Interest rate is required')
        .refine((v) => Number(v) > 0 && Number(v) <= 100, '0–100%'),
    term_months: z
        .string()
        .min(1, 'Term is required')
        .refine((v) => Number(v) >= 1 && Number(v) <= 360, '1–360 months'),
    purpose: z.string().min(10, 'At least 10 characters'),
    // AI scoring fields
    person_age: z
        .string()
        .min(1, 'Age is required')
        .refine((v) => Number(v) >= 18 && Number(v) <= 100, '18–100'),
    person_income: z
        .string()
        .min(1, 'Income is required')
        .refine((v) => Number(v) >= 1000 && Number(v) <= 10000000, '1,000–10,000,000'),
    person_home_ownership: z.enum(['RENT', 'MORTGAGE', 'OWN', 'OTHER'], {
        error: () => ({ message: 'Required' }),
    }),
    person_emp_length: z
        .string()
        .min(1, 'Required')
        .refine((v) => Number(v) >= 0 && Number(v) <= 50, '0–50 years'),
    loan_intent: z.enum(['PERSONAL', 'EDUCATION', 'MEDICAL', 'VENTURE', 'HOMEIMPROVEMENT', 'DEBTCONSOLIDATION'], {
        error: () => ({ message: 'Required' }),
    }),
    loan_grade: z.enum(['A', 'B', 'C', 'D', 'E', 'F', 'G'], {
        error: () => ({ message: 'Required' }),
    }),
    cb_person_default_on_file: z.enum(['Y', 'N'], {
        error: () => ({ message: 'Required' }),
    }),
    cb_person_cred_hist_length: z
        .string()
        .min(1, 'Required')
        .refine((v) => Number(v) >= 0 && Number(v) <= 50, '0–50 years'),
});

type CreateLoanForm = z.infer<typeof createLoanSchema>;

const intentOptions = [
    { label: 'Personal', value: 'PERSONAL' },
    { label: 'Education', value: 'EDUCATION' },
    { label: 'Medical', value: 'MEDICAL' },
    { label: 'Venture', value: 'VENTURE' },
    { label: 'Home Improvement', value: 'HOMEIMPROVEMENT' },
    { label: 'Debt Consolidation', value: 'DEBTCONSOLIDATION' },
];

const ownershipOptions = [
    { label: 'Rent', value: 'RENT' },
    { label: 'Mortgage', value: 'MORTGAGE' },
    { label: 'Own', value: 'OWN' },
    { label: 'Other', value: 'OTHER' },
];

const gradeOptions = ['A', 'B', 'C', 'D', 'E', 'F', 'G'].map((g) => ({ label: `Grade ${g}`, value: g }));

const defaultOptions = [
    { label: 'No', value: 'N' },
    { label: 'Yes', value: 'Y' },
];

export function LoanCreatePage() {
    const navigate = useNavigate();
    const createLoan = useCreateLoan();

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
        defaultValues: { cb_person_default_on_file: 'N' },
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
            interest_rate: Number(data.interest_rate) / 100, // % → decimal
            term_months: Number(data.term_months),
            purpose: data.purpose,
            person_age: Number(data.person_age),
            person_income: Number(data.person_income),
            person_home_ownership: data.person_home_ownership,
            person_emp_length: Number(data.person_emp_length),
            loan_intent: data.loan_intent,
            loan_grade: data.loan_grade,
            cb_person_default_on_file: data.cb_person_default_on_file,
            cb_person_cred_hist_length: Number(data.cb_person_cred_hist_length),
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
                    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-6">
                        {/* ── Basic loan info ── */}
                        <div>
                            <p className="text-xs font-medium text-text-secondary uppercase tracking-wide mb-3">Loan Details</p>
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
                                <Input
                                    label="Interest Rate (%)"
                                    type="number"
                                    step="0.01"
                                    placeholder="e.g. 8.5"
                                    error={errors.interest_rate?.message}
                                    {...register('interest_rate')}
                                />
                                <Input
                                    label="Term (months)"
                                    type="number"
                                    error={errors.term_months?.message}
                                    {...register('term_months')}
                                />
                                <Input
                                    label="Purpose"
                                    placeholder="e.g. Home renovation project funding"
                                    error={errors.purpose?.message}
                                    {...register('purpose')}
                                />
                                <Select
                                    label="Loan Intent"
                                    placeholder="Select intent"
                                    options={intentOptions}
                                    error={errors.loan_intent?.message}
                                    {...register('loan_intent')}
                                />
                                <Select
                                    label="Loan Grade"
                                    placeholder="Select grade"
                                    options={gradeOptions}
                                    error={errors.loan_grade?.message}
                                    {...register('loan_grade')}
                                />
                            </div>
                        </div>

                        {/* ── AI scoring fields ── */}
                        <div>
                            <p className="text-xs font-medium text-text-secondary uppercase tracking-wide mb-3">Applicant Profile (AI Scoring)</p>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <Input
                                    label="Age"
                                    type="number"
                                    placeholder="18–100"
                                    error={errors.person_age?.message}
                                    {...register('person_age')}
                                />
                                <Input
                                    label="Annual Income"
                                    type="number"
                                    placeholder="1,000–10,000,000"
                                    error={errors.person_income?.message}
                                    {...register('person_income')}
                                />
                                <Select
                                    label="Home Ownership"
                                    placeholder="Select"
                                    options={ownershipOptions}
                                    error={errors.person_home_ownership?.message}
                                    {...register('person_home_ownership')}
                                />
                                <Input
                                    label="Employment Length (years)"
                                    type="number"
                                    placeholder="0–50"
                                    error={errors.person_emp_length?.message}
                                    {...register('person_emp_length')}
                                />
                                <Input
                                    label="Credit History Length (years)"
                                    type="number"
                                    placeholder="0–50"
                                    error={errors.cb_person_cred_hist_length?.message}
                                    {...register('cb_person_cred_hist_length')}
                                />
                                <Select
                                    label="Previous Default on File"
                                    options={defaultOptions}
                                    error={errors.cb_person_default_on_file?.message}
                                    {...register('cb_person_default_on_file')}
                                />
                            </div>
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
