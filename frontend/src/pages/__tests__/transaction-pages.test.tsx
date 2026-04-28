import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { TransactionListPage } from '~/pages/TransactionListPage/TransactionListPage';
import { TransactionDetailPage } from '~/pages/TransactionDetailPage/TransactionDetailPage';
import { TransactionSubmitPage } from '~/pages/TransactionSubmitPage/TransactionSubmitPage';
import { createMutationResult, createQueryResult, navigateMock, setRouteParams } from '~/test/testUtils';
import {
    transactionDetail,
    transactionListItem,
    transactionListResponse,
    transactionStates,
    transactionSubmitResponse,
} from '~/test/fixtures';

const transactionHookMocks = vi.hoisted(() => ({
    useTransactions: vi.fn(),
    useTransaction: vi.fn(),
    useTransactionStates: vi.fn(),
    useSubmitTransaction: vi.fn(),
    useDemoRunning: vi.fn(),
}));

vi.mock('~/hooks/useTransactions', () => ({
    useTransactions: transactionHookMocks.useTransactions,
    useTransaction: transactionHookMocks.useTransaction,
    useTransactionStates: transactionHookMocks.useTransactionStates,
    useSubmitTransaction: transactionHookMocks.useSubmitTransaction,
}));

vi.mock('~/hooks/useDemoRunning', () => ({
    useDemoRunning: transactionHookMocks.useDemoRunning,
}));

describe('transaction pages', () => {
    beforeEach(() => {
        transactionHookMocks.useTransactions.mockReset();
        transactionHookMocks.useTransaction.mockReset();
        transactionHookMocks.useTransactionStates.mockReset();
        transactionHookMocks.useSubmitTransaction.mockReset();
        transactionHookMocks.useDemoRunning.mockReset();
        setRouteParams({});
    });

    it('renders the transaction list and navigates on row click', async () => {
        const user = userEvent.setup();
        transactionHookMocks.useDemoRunning.mockReturnValue(false);
        transactionHookMocks.useTransactions.mockReturnValue(createQueryResult(transactionListResponse));

        render(<TransactionListPage />);

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

    it('renders the transaction detail and state history', async () => {
        const user = userEvent.setup();
        transactionHookMocks.useTransaction.mockReturnValue(createQueryResult(transactionDetail));
        transactionHookMocks.useTransactionStates.mockReturnValue(createQueryResult(transactionStates));
        setRouteParams({ txnId: transactionDetail.txn_id });

        render(<TransactionDetailPage />);

        expect(screen.getByRole('heading', { name: 'Transaction Detail' })).toBeInTheDocument();
        expect(screen.getByText('Transaction Details')).toBeInTheDocument();
        expect(screen.getByText('State History')).toBeInTheDocument();
        expect(screen.getByText('Reason')).toBeInTheDocument();
        expect(screen.getAllByText('MANUAL_REVIEW').length).toBeGreaterThan(0);

        await user.click(screen.getByRole('button', { name: 'Back to List' }));
        expect(navigateMock).toHaveBeenLastCalledWith({ to: '/transactions' });
    });

    it('submits a transaction and navigates to the new detail page', async () => {
        const user = userEvent.setup();
        const submitMutation = createMutationResult({ data: transactionSubmitResponse });
        transactionHookMocks.useSubmitTransaction.mockReturnValue(submitMutation);

        render(<TransactionSubmitPage />);

        await user.type(screen.getByLabelText('Customer ID'), 'cust-900');
        await user.type(screen.getByLabelText('Merchant ID'), 'mer-900');
        await user.type(screen.getByLabelText('Channel ID'), '2');
        await user.type(screen.getByLabelText('Card Number (masked)'), '4111********9000');
        await user.type(screen.getByLabelText('Amount'), '2500');
        await user.clear(screen.getByLabelText('Transaction Time'));
        await user.type(screen.getByLabelText('Transaction Time'), '2025-04-20T08:30');
        await user.type(screen.getByLabelText('Source IP'), '192.0.2.10');
        await user.click(screen.getByRole('button', { name: 'Submit for Scoring' }));

        const expectedTxnTime = new Date('2025-04-20T08:30').toISOString();

        expect(submitMutation.mutate).toHaveBeenCalledWith(
            {
                customer_id: 'cust-900',
                merchant_id: 'mer-900',
                channel_id: 2,
                card_number_masked: '4111********9000',
                amount: 2500,
                currency_code: 'VND',
                txn_time: expectedTxnTime,
                source_ip: '192.0.2.10',
            },
            expect.any(Object),
        );
        expect(navigateMock).toHaveBeenLastCalledWith({
            to: '/transactions/$txnId',
            params: { txnId: transactionSubmitResponse.txn_id },
        });
    });
});
