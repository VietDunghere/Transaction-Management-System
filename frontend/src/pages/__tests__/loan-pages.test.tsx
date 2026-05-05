import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { LoanListPage } from '~/pages/LoanListPage/LoanListPage';
import { LoanCreatePage } from '~/pages/LoanCreatePage/LoanCreatePage';
import { LoanSimulatePage } from '~/pages/LoanSimulatePage/LoanSimulatePage';
import { LoanDetailPage } from '~/pages/LoanDetailPage/LoanDetailPage';
import {
    loanCreateResponse,
    loanDetail,
    loanListResponse,
    loanSimulationResponse,
    operatorUser,
    reviewerUser,
} from '~/test/fixtures';
import { createMutationResult, createQueryResult, navigateMock, setAuthUser, setRouteParams } from '~/test/testUtils';

const loanHookMocks = vi.hoisted(() => ({
    useLoans: vi.fn(),
    useLoan: vi.fn(),
    useCreateLoan: vi.fn(),
    useSimulateLoan: vi.fn(),
    useDecideLoan: vi.fn(),
    useDemoRunning: vi.fn(),
}));

vi.mock('~/hooks/useLoans', () => ({
    useLoans: loanHookMocks.useLoans,
    useLoan: loanHookMocks.useLoan,
    useCreateLoan: loanHookMocks.useCreateLoan,
    useSimulateLoan: loanHookMocks.useSimulateLoan,
    useDecideLoan: loanHookMocks.useDecideLoan,
}));

vi.mock('~/hooks/useDemoRunning', () => ({
    useDemoRunning: loanHookMocks.useDemoRunning,
}));

describe('loan pages', () => {
    beforeEach(() => {
        loanHookMocks.useLoans.mockReset();
        loanHookMocks.useLoan.mockReset();
        loanHookMocks.useCreateLoan.mockReset();
        loanHookMocks.useSimulateLoan.mockReset();
        loanHookMocks.useDecideLoan.mockReset();
        loanHookMocks.useDemoRunning.mockReset();
        setRouteParams({});
        setAuthUser(null);
    });

    it('renders the loan list and exposes operator actions', async () => {
        const user = userEvent.setup();
        loanHookMocks.useDemoRunning.mockReturnValue(false);
        loanHookMocks.useLoans.mockReturnValue(createQueryResult(loanListResponse));
        setAuthUser(operatorUser);

        render(<LoanListPage />);

        expect(screen.getByRole('heading', { name: 'Loans' })).toBeInTheDocument();
        expect(screen.getByText('1 total loans')).toBeInTheDocument();
        expect(screen.getByText('Create Loan')).toBeInTheDocument();
        expect(screen.getByText('Simulate')).toBeInTheDocument();
        expect(screen.getByText('loan-001...')).toBeInTheDocument();

        await user.click(screen.getByText('loan-001...'));
        expect(navigateMock).toHaveBeenLastCalledWith({
            to: '/loans/$loanId',
            params: { loanId: loanListResponse.data[0].loan_id },
        });
    });

    it('creates a loan application and navigates to the loan detail page', async () => {
        const user = userEvent.setup();
        const createLoanMutation = createMutationResult({ data: loanCreateResponse });
        loanHookMocks.useCreateLoan.mockReturnValue(createLoanMutation);

        render(<LoanCreatePage />);

        await user.type(screen.getByLabelText('Customer ID'), 'cust-900');
        await user.type(screen.getByLabelText('Principal Amount'), '300000');
        await user.type(screen.getByLabelText('Interest Rate (%)'), '11.5');
        await user.type(screen.getByLabelText('Term (months)'), '36');
        await user.type(screen.getByLabelText('Purpose'), 'Home Improvement');
        await user.click(screen.getByRole('button', { name: 'Submit Loan' }));

        expect(createLoanMutation.mutate).toHaveBeenCalledWith(
            {
                customer_id: 'cust-900',
                principal_amount: 300000,
                interest_rate: 11.5,
                term_months: 36,
                purpose: 'Home Improvement',
            },
            expect.any(Object),
        );
        expect(navigateMock).toHaveBeenLastCalledWith({
            to: '/loans/$loanId',
            params: { loanId: loanCreateResponse.loan_id },
        });
    });

    it('runs a simulation and shows the computed result card', async () => {
        const user = userEvent.setup();
        let isSuccess = false;
        const simulateMutation = {
            get isSuccess() {
                return isSuccess;
            },
            isPending: false,
            isError: false,
            data: loanSimulationResponse,
            mutate: vi.fn((variables: unknown, callbacks?: { onSuccess?: (data: unknown) => void }) => {
                isSuccess = true;
                callbacks?.onSuccess?.(loanSimulationResponse);
                return variables;
            }),
        };
        loanHookMocks.useSimulateLoan.mockReturnValue(simulateMutation);

        render(<LoanSimulatePage />);

        await user.type(screen.getByLabelText('Age'), '34');
        await user.type(screen.getByLabelText('Annual Income'), '120000');
        await user.selectOptions(screen.getByLabelText('Home Ownership'), 'OWN');
        await user.type(screen.getByLabelText('Employment Length (years)'), '8');
        await user.type(screen.getByLabelText('Loan Amount'), '250000');
        await user.selectOptions(screen.getByLabelText('Loan Grade'), 'B');
        await user.selectOptions(screen.getByLabelText('Loan Intent'), 'DEBTCONSOLIDATION');
        await user.selectOptions(screen.getByLabelText('Default on File'), 'N');
        await user.type(screen.getByLabelText('Credit History Length (years)'), '12');
        await user.type(screen.getByLabelText('Requested Term (months)'), '24');
        await user.click(screen.getByRole('button', { name: 'Run Simulation' }));

        expect(simulateMutation.mutate).toHaveBeenCalledWith(
            {
                person_age: 34,
                person_income: 120000,
                person_home_ownership: 'OWN',
                person_emp_length: 8,
                loan_amount: 250000,
                loan_grade: 'B',
                loan_intent: 'DEBTCONSOLIDATION',
                cb_person_default_on_file: 'N',
                cb_person_cred_hist_length: 12,
                requested_term_months: 24,
            },
            expect.any(Object),
        );
        expect(screen.getByText('Simulation Results')).toBeInTheDocument();
        expect(screen.getByText('APPROVE')).toBeInTheDocument();
    });

    it('shows loan detail review actions for a reviewer', async () => {
        const user = userEvent.setup();
        const decideLoanMutation = createMutationResult({ data: { loan_id: loanDetail.loan_id } });
        loanHookMocks.useLoan.mockReturnValue(createQueryResult(loanDetail));
        loanHookMocks.useDecideLoan.mockReturnValue(decideLoanMutation);
        loanHookMocks.useCreateLoan.mockReturnValue(createMutationResult());
        setAuthUser(reviewerUser);
        setRouteParams({ loanId: loanDetail.loan_id });

        render(<LoanDetailPage />);

        expect(screen.getByRole('heading', { name: 'Loan Detail' })).toBeInTheDocument();
        expect(screen.getByText('Loan Details')).toBeInTheDocument();
        expect(screen.getByText('Loan History (This Bank)')).toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'Approve' })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'Reject' })).toBeInTheDocument();

        await user.click(screen.getByRole('button', { name: 'Approve' }));
        expect(screen.getByText('Approve Loan')).toBeInTheDocument();
        await user.type(screen.getByLabelText('Review Note (required)'), 'Applicant meets the policy requirements');
        await user.click(screen.getByRole('button', { name: 'Confirm Approval' }));

        expect(decideLoanMutation.mutate).toHaveBeenCalledWith(
            {
                loanId: loanDetail.loan_id,
                decision: 'APPROVE',
                review_note: 'Applicant meets the policy requirements',
                version: loanDetail.version,
            },
            expect.any(Object),
        );
    });
});
