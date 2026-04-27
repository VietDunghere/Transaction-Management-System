import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useSimulateLoan } from '~/hooks/useLoans';
import type { RiskLevel } from '~/types/api';
import { riskLabel } from '~/types/api';
import { PageHeader } from '~/components/templates/PageHeader/PageHeader';
import { FormPageTemplate } from '~/components/templates/FormPageTemplate/FormPageTemplate';
import { Card } from '~/components/ui/Card/Card';
import { Input } from '~/components/ui/Input/Input';
import { Select } from '~/components/ui/Select/Select';
import { Button } from '~/components/ui/Button/Button';
import { Badge } from '~/components/ui/Badge/Badge';
import { StatCard } from '~/components/ui/StatCard/StatCard';
import { SectionHeader } from '~/components/ui/SectionHeader/SectionHeader';

const simulateSchema = z.object({
    person_age: z.string().min(1, 'Age is required'),
    person_income: z.string().min(1, 'Income is required'),
    person_home_ownership: z.string().min(1, 'Home ownership is required'),
    person_emp_length: z.string().min(1, 'Employment length is required'),
    loan_amount: z.string().min(1, 'Loan amount is required'),
    loan_grade: z.string().min(1, 'Loan grade is required'),
    loan_intent: z.string().min(1, 'Loan intent is required'),
    cb_person_default_on_file: z.string().min(1, 'Default on file is required'),
    cb_person_cred_hist_length: z.string().min(1, 'Credit history length is required'),
    requested_term_months: z.string().min(1, 'Term is required'),
});

type SimulateForm = z.infer<typeof simulateSchema>;

const homeOwnershipOptions = [
    { label: 'Select...', value: '' },
    { label: 'RENT', value: 'RENT' },
    { label: 'OWN', value: 'OWN' },
    { label: 'MORTGAGE', value: 'MORTGAGE' },
    { label: 'OTHER', value: 'OTHER' },
];

const gradeOptions = [
    { label: 'Select...', value: '' },
    { label: 'A', value: 'A' },
    { label: 'B', value: 'B' },
    { label: 'C', value: 'C' },
    { label: 'D', value: 'D' },
    { label: 'E', value: 'E' },
    { label: 'F', value: 'F' },
    { label: 'G', value: 'G' },
];

const intentOptions = [
    { label: 'Select...', value: '' },
    { label: 'Education', value: 'EDUCATION' },
    { label: 'Medical', value: 'MEDICAL' },
    { label: 'Personal', value: 'PERSONAL' },
    { label: 'Venture', value: 'VENTURE' },
    { label: 'Home Improvement', value: 'HOMEIMPROVEMENT' },
    { label: 'Debt Consolidation', value: 'DEBTCONSOLIDATION' },
];

const defaultOnFileOptions = [
    { label: 'Select...', value: '' },
    { label: 'Yes', value: 'Y' },
    { label: 'No', value: 'N' },
];

const riskVariant: Record<RiskLevel, 'success' | 'warning' | 'danger'> = {
    'LOW RISK': 'success',
    'MEDIUM RISK': 'warning',
    'HIGH RISK': 'danger',
};

export function LoanSimulatePage() {
    const simulateLoan = useSimulateLoan();
    const [showResult, setShowResult] = useState(false);

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<SimulateForm>({
        resolver: zodResolver(simulateSchema),
    });

    const onSubmit = (data: SimulateForm) => {
        simulateLoan.mutate(
            {
                person_age: Number(data.person_age),
                person_income: Number(data.person_income),
                person_home_ownership: data.person_home_ownership,
                person_emp_length: Number(data.person_emp_length),
                loan_amount: Number(data.loan_amount),
                loan_grade: data.loan_grade,
                loan_intent: data.loan_intent,
                cb_person_default_on_file: data.cb_person_default_on_file,
                cb_person_cred_hist_length: Number(data.cb_person_cred_hist_length),
                requested_term_months: Number(data.requested_term_months),
            },
            {
                onSuccess: () => setShowResult(true),
            },
        );
    };

    return (
        <FormPageTemplate
            header={<PageHeader title="Loan Simulator" subtitle="Estimate loan risk and probability of default" />}
            form={
                <Card>
                    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
                        <SectionHeader title="Applicant Information" />
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <Input
                                label="Age"
                                type="number"
                                error={errors.person_age?.message}
                                {...register('person_age')}
                            />
                            <Input
                                label="Annual Income"
                                type="number"
                                error={errors.person_income?.message}
                                {...register('person_income')}
                            />
                            <Select
                                label="Home Ownership"
                                options={homeOwnershipOptions}
                                error={errors.person_home_ownership?.message}
                                {...register('person_home_ownership')}
                            />
                            <Input
                                label="Employment Length (years)"
                                type="number"
                                error={errors.person_emp_length?.message}
                                {...register('person_emp_length')}
                            />
                        </div>

                        <SectionHeader title="Loan Information" />
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <Input
                                label="Loan Amount"
                                type="number"
                                error={errors.loan_amount?.message}
                                {...register('loan_amount')}
                            />
                            <Select
                                label="Loan Grade"
                                options={gradeOptions}
                                error={errors.loan_grade?.message}
                                {...register('loan_grade')}
                            />
                            <Select
                                label="Loan Intent"
                                options={intentOptions}
                                error={errors.loan_intent?.message}
                                {...register('loan_intent')}
                            />
                            <Input
                                label="Requested Term (months)"
                                type="number"
                                error={errors.requested_term_months?.message}
                                {...register('requested_term_months')}
                            />
                        </div>

                        <SectionHeader title="Credit History" />
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <Select
                                label="Default on File"
                                options={defaultOnFileOptions}
                                error={errors.cb_person_default_on_file?.message}
                                {...register('cb_person_default_on_file')}
                            />
                            <Input
                                label="Credit History Length (years)"
                                type="number"
                                error={errors.cb_person_cred_hist_length?.message}
                                {...register('cb_person_cred_hist_length')}
                            />
                        </div>

                        {simulateLoan.isError && (
                            <p className="text-xs text-status-danger">
                                Simulation failed. Please check your inputs and try again.
                            </p>
                        )}

                        <div className="flex justify-end">
                            <Button type="submit" loading={simulateLoan.isPending}>
                                Run Simulation
                            </Button>
                        </div>
                    </form>
                </Card>
            }
            footer={
                showResult && simulateLoan.isSuccess ? (
                    <Card>
                        <SectionHeader title="Simulation Results" />
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                            <StatCard label="PD Score" value={`${(simulateLoan.data.pd_score * 100).toFixed(1)}%`} />
                            <StatCard label="Risk Level" value={riskLabel[simulateLoan.data.risk_level as RiskLevel]} />
                            <StatCard label="Decision" value={simulateLoan.data.decision} />
                            <StatCard
                                label="Confidence"
                                value={`${(simulateLoan.data.confidence * 100).toFixed(1)}%`}
                            />
                        </div>
                        <div className="mt-4 p-3 rounded-sm bg-secondary">
                            <Badge variant={riskVariant[simulateLoan.data.risk_level as RiskLevel]}>
                                {riskLabel[simulateLoan.data.risk_level as RiskLevel]}
                            </Badge>
                            <span className="text-sm ml-2">
                                {simulateLoan.data.decision === 'APPROVE'
                                    ? 'This loan application is likely to be approved.'
                                    : 'This loan application may require further review.'}
                            </span>
                        </div>
                    </Card>
                ) : (
                    <div />
                )
            }
        />
    );
}
