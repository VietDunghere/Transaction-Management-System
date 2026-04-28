import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { CaseListPage } from '~/pages/CaseListPage/CaseListPage';
import { CaseDetailPage } from '~/pages/CaseDetailPage/CaseDetailPage';
import { createMutationResult, createQueryResult, navigateMock, setAuthUser, setRouteParams } from '~/test/testUtils';
import { caseDetail, caseListResponse, caseDecisionResponse, reviewerUser } from '~/test/fixtures';

const caseHookMocks = vi.hoisted(() => ({
    useCases: vi.fn(),
    useCase: vi.fn(),
    useAssignCase: vi.fn(),
    useDecideCase: vi.fn(),
    useDemoRunning: vi.fn(),
}));

vi.mock('~/hooks/useCases', () => ({
    useCases: caseHookMocks.useCases,
    useCase: caseHookMocks.useCase,
    useAssignCase: caseHookMocks.useAssignCase,
    useDecideCase: caseHookMocks.useDecideCase,
}));

vi.mock('~/hooks/useDemoRunning', () => ({
    useDemoRunning: caseHookMocks.useDemoRunning,
}));

describe('case pages', () => {
    beforeEach(() => {
        caseHookMocks.useCases.mockReset();
        caseHookMocks.useCase.mockReset();
        caseHookMocks.useAssignCase.mockReset();
        caseHookMocks.useDecideCase.mockReset();
        caseHookMocks.useDemoRunning.mockReset();
        setRouteParams({});
        setAuthUser(null);
    });

    it('renders the case list and opens the case detail route', async () => {
        const user = userEvent.setup();
        caseHookMocks.useDemoRunning.mockReturnValue(false);
        caseHookMocks.useCases.mockReturnValue(createQueryResult(caseListResponse));

        render(<CaseListPage />);

        expect(screen.getByRole('heading', { name: 'Cases' })).toBeInTheDocument();
        expect(screen.getByText('1 total cases')).toBeInTheDocument();
        expect(screen.getByText('case-001...')).toBeInTheDocument();
        expect(screen.getByText('OPEN')).toBeInTheDocument();

        await user.click(screen.getByText('case-001...'));
        expect(navigateMock).toHaveBeenLastCalledWith({
            to: '/cases/$caseId',
            params: { caseId: caseListResponse.data[0].case_id },
        });
    });

    it('assigns an open case to the reviewer', async () => {
        const user = userEvent.setup();
        const assignMutation = createMutationResult();
        caseHookMocks.useCase.mockReturnValue(createQueryResult(caseDetail));
        caseHookMocks.useAssignCase.mockReturnValue(assignMutation);
        caseHookMocks.useDecideCase.mockReturnValue(createMutationResult({ data: caseDecisionResponse }));
        setAuthUser(reviewerUser);
        setRouteParams({ caseId: caseDetail.case_id });

        render(<CaseDetailPage />);

        expect(screen.getByRole('heading', { name: 'Case Detail' })).toBeInTheDocument();
        expect(screen.getByText('Case Details')).toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'Assign to Me' })).toBeInTheDocument();

        await user.click(screen.getByRole('button', { name: 'Assign to Me' }));
        expect(assignMutation.mutate).toHaveBeenCalledWith(caseDetail.case_id);
        expect(screen.getByText('Triggered Rules (1)')).toBeInTheDocument();
        expect(screen.getByText('Card Velocity')).toBeInTheDocument();
    });

    it('submits a decision for an assigned case', async () => {
        const user = userEvent.setup();
        const decideMutation = createMutationResult({ data: caseDecisionResponse });
        caseHookMocks.useCase.mockReturnValue(
            createQueryResult({
                ...caseDetail,
                case_status: 'ASSIGNED',
                assigned_to: reviewerUser.user_id,
                assigned_to_name: reviewerUser.full_name,
            }),
        );
        caseHookMocks.useAssignCase.mockReturnValue(createMutationResult());
        caseHookMocks.useDecideCase.mockReturnValue(decideMutation);
        setAuthUser(reviewerUser);
        setRouteParams({ caseId: caseDetail.case_id });

        render(<CaseDetailPage />);

        await user.click(screen.getByRole('button', { name: 'Approve' }));
        expect(screen.getByText('Approve Case')).toBeInTheDocument();
        await user.type(screen.getByLabelText('Decision Note (required, min 10 characters)'), 'Manual review cleared');
        await user.click(screen.getByRole('button', { name: 'Confirm Approval' }));

        expect(decideMutation.mutate).toHaveBeenCalledWith(
            {
                caseId: caseDetail.case_id,
                decision: 'APPROVE',
                decision_note: 'Manual review cleared',
                version: caseDetail.version,
            },
            expect.any(Object),
        );
    });
});
