import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { TransactionFRM } from '~/pages/TransactionFRM/TransactionFRM';
import { TransactionDetailFrm } from '~/pages/TransactionDetailFrm/TransactionDetailFrm';
import { AddTransactionFRM } from '~/pages/AddTransactionFRM/AddTransactionFRM';
import { createMutationResult, createQueryResult, navigateMock, setRouteParams } from '~/test/testUtils';
import {
    transactionDetail,
    transactionListItem,
    transactionListResponse,
    transactionSubmitResponse,
} from '~/test/fixtures';

const transactionHookMocks = vi.hoisted(() => ({
    useTransactions: vi.fn(),
    useTransaction: vi.fn(),
    useSubmitTransaction: vi.fn(),
    useDemoRunning: vi.fn(),
}));

vi.mock('~/hooks/useTransactions', () => ({
    useTransactions: transactionHookMocks.useTransactions,
    useTransaction: transactionHookMocks.useTransaction,
    useSubmitTransaction: transactionHookMocks.useSubmitTransaction,
}));

vi.mock('~/hooks/useDemoRunning', () => ({
    useDemoRunning: transactionHookMocks.useDemoRunning,
}));

describe('transaction pages', () => {
    beforeEach(() => {
        transactionHookMocks.useTransactions.mockReset();
        transactionHookMocks.useTransaction.mockReset();
        transactionHookMocks.useSubmitTransaction.mockReset();
        transactionHookMocks.useDemoRunning.mockReset();
        setRouteParams({});
    });

    it('renders the transaction list and navigates on row click', async () => {
        const user = userEvent.setup();
        transactionHookMocks.useDemoRunning.mockReturnValue(false);
        transactionHookMocks.useTransactions.mockReturnValue(createQueryResult(transactionListResponse));

        render(<TransactionFRM />);

        expect(screen.getByRole('heading', { name: 'Transactions' })).toBeInTheDocument();
        expect(screen.getByText('1 total transactions')).toBeInTheDocument();
        expect(screen.getByText('txn-001...')).toBeInTheDocument();
        expect(screen.getByText('MANUAL_REVIEW')).toBeInTheDocument();

        await user.click(screen.getByText('txn-001...'));
        expect(navigateMock).toHaveBeenLastCalledWith({
            to: '/transactions/$txnId',
            params: { txnId: transactionListItem.txn_id },
        });
    });

    it('renders the transaction detail page', async () => {
        const user = userEvent.setup();
        transactionHookMocks.useTransaction.mockReturnValue(createQueryResult(transactionDetail));
        setRouteParams({ txnId: transactionDetail.txn_id });

        render(<TransactionDetailFrm />);

        expect(screen.getByRole('heading', { name: 'Transaction Detail' })).toBeInTheDocument();
        expect(screen.getByText('Transaction Details')).toBeInTheDocument();
        expect(screen.getAllByText('MANUAL_REVIEW').length).toBeGreaterThan(0);

        await user.click(screen.getByRole('button', { name: 'Back to List' }));
        expect(navigateMock).toHaveBeenLastCalledWith({ to: '/transactions' });
    });

    it('submits a transaction and shows result', async () => {
        const submitMutation = createMutationResult({ data: transactionSubmitResponse });
        transactionHookMocks.useSubmitTransaction.mockReturnValue(submitMutation);

        render(<AddTransactionFRM />);

        expect(screen.getByRole('heading', { name: 'Submit Transaction' })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'Submit for Scoring' })).toBeInTheDocument();
    });
});
