import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate } from '@tanstack/react-router';
import { useCreateLoan } from '~/hooks/useLoans';
import { PageHeader } from '~/components/templates/PageHeader/PageHeader';
import { FormPageTemplate } from '~/components/templates/FormPageTemplate/FormPageTemplate';
import { Card } from '~/components/ui/Card/Card';
import { Input } from '~/components/ui/Input/Input';
import { Select } from '~/components/ui/Select/Select';
import { Button } from '~/components/ui/Button/Button';

const createLoanSchema = z.object({
    customer_id: z.string().min(1, 'Customer ID is required'),
    principal_amount: z.string().min(1, 'Principal amount is required'),
    currency_code: z.string().min(1, 'Currency is required'),
    interest_rate: z.string().min(1, 'Interest rate is required'),
    term_months: z.string().min(1, 'Term is required'),
    purpose: z.string().min(1, 'Purpose is required'),
});

type CreateLoanForm = z.infer<typeof createLoanSchema>;

const currencyOptions = [
    { label: 'VND', value: 'VND' },
    { label: 'USD', value: 'USD' },
];

export function LoanCreatePage() {
    const navigate = useNavigate();
    const createLoan = useCreateLoan();

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<CreateLoanForm>({
        resolver: zodResolver(createLoanSchema),
        defaultValues: {
            currency_code: 'VND',
        },
    });

    const onSubmit = (data: CreateLoanForm) => {
        createLoan.mutate(
            {
                customer_id: data.customer_id,
                principal_amount: Number(data.principal_amount),
                currency_code: data.currency_code,
                interest_rate: Number(data.interest_rate),
                term_months: Number(data.term_months),
                purpose: data.purpose,
            },
            {
                onSuccess: (res) => {
                    navigate({ to: '/loans/$loanId', params: { loanId: res.loan_id } });
                },
            },
        );
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
                            <Input
                                label="Customer ID"
                                error={errors.customer_id?.message}
                                {...register('customer_id')}
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
                            <Input
                                label="Purpose"
                                error={errors.purpose?.message}
                                {...register('purpose')}
                            />
                        </div>

                        {createLoan.isError && (
                            <p className="text-xs text-status-danger">
                                Failed to create loan. Please try again.
                            </p>
                        )}

                        <div className="flex justify-end">
                            <Button type="submit" loading={createLoan.isPending}>
                                Submit Loan
                            </Button>
                        </div>
                    </form>
                </Card>
            }
            footer={<div />}
        />
    );
}
