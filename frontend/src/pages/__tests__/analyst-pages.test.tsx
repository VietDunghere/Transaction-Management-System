import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AnalystThresholdsPage } from '~/pages/AnalystThresholdsPage/AnalystThresholdsPage';
import { AnalystModelPerformancePage } from '~/pages/AnalystModelPerformancePage/AnalystModelPerformancePage';
import { analystUser, fraudPerformance, loanPerformance, thresholds } from '~/test/fixtures';
import { createMutationResult, createQueryResult, setAuthUser } from '~/test/testUtils';

const analystHookMocks = vi.hoisted(() => ({
    useThresholds: vi.fn(),
    useUpdateThresholds: vi.fn(),
    useFraudPerformance: vi.fn(),
    useLoanPerformance: vi.fn(),
}));

vi.mock('~/hooks/useAnalyst', () => ({
    useThresholds: analystHookMocks.useThresholds,
    useUpdateThresholds: analystHookMocks.useUpdateThresholds,
    useFraudPerformance: analystHookMocks.useFraudPerformance,
    useLoanPerformance: analystHookMocks.useLoanPerformance,
}));

describe('analyst pages', () => {
    beforeEach(() => {
        analystHookMocks.useThresholds.mockReset();
        analystHookMocks.useUpdateThresholds.mockReset();
        analystHookMocks.useFraudPerformance.mockReset();
        analystHookMocks.useLoanPerformance.mockReset();
        setAuthUser(null);
    });

    it('renders thresholds and saves a fraud model update', async () => {
        const user = userEvent.setup();
        const updateThresholdsMutation = createMutationResult();
        analystHookMocks.useThresholds.mockReturnValue(createQueryResult(thresholds));
        analystHookMocks.useUpdateThresholds.mockReturnValue(updateThresholdsMutation);
        setAuthUser(analystUser);

        render(<AnalystThresholdsPage />);

        expect(screen.getByRole('heading', { name: 'Model Thresholds' })).toBeInTheDocument();
        expect(screen.getByText('Fraud Detection Model')).toBeInTheDocument();
        expect(screen.getByText('Loan PD Score Model')).toBeInTheDocument();

        await user.click(screen.getAllByRole('button', { name: 'Edit' })[0]);
        expect(screen.getByText('Update Threshold')).toBeInTheDocument();
        await user.clear(screen.getByLabelText(/New Value/));
        await user.type(screen.getByLabelText(/New Value/), '0.70');
        await user.click(screen.getByRole('button', { name: 'Save' }));

        expect(updateThresholdsMutation.mutate).toHaveBeenCalledWith(
            {
                updates: [
                    {
                        model_name: 'fraud',
                        param_name: 'reject_threshold',
                        param_value: 0.7,
                    },
                ],
            },
            expect.any(Object),
        );
    });

    it('switches between performance tabs and renders both chart states', async () => {
        const user = userEvent.setup();
        analystHookMocks.useFraudPerformance.mockReturnValue(createQueryResult(fraudPerformance));
        analystHookMocks.useLoanPerformance.mockReturnValue(createQueryResult(loanPerformance));

        render(<AnalystModelPerformancePage />);

        expect(screen.getByRole('heading', { name: 'Model Performance' })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'Fraud Model' })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'Loan Model' })).toBeInTheDocument();
        expect(screen.getAllByRole('heading', { name: 'Score Distribution' }).length).toBeGreaterThan(0);
        expect(screen.getByText('False Positives')).toBeInTheDocument();
        expect(screen.getByText('Current Thresholds')).toBeInTheDocument();

        await user.click(screen.getByRole('button', { name: 'Loan Model' }));
        expect(screen.getByRole('heading', { name: 'Risk Distribution' })).toBeInTheDocument();
        expect(screen.getByText('Loan Outcomes')).toBeInTheDocument();
    });
});
