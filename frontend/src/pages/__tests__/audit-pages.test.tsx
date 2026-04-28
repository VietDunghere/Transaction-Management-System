import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuditLogListPage } from '~/pages/AuditLogListPage/AuditLogListPage';
import { AuditLogDetailPage } from '~/pages/AuditLogDetailPage/AuditLogDetailPage';
import { auditLogDetail, auditLogListResponse } from '~/test/fixtures';
import { createQueryResult, navigateMock, setRouteParams } from '~/test/testUtils';

const auditHookMocks = vi.hoisted(() => ({
    useAuditLogs: vi.fn(),
    useAuditLog: vi.fn(),
}));

vi.mock('~/hooks/useAuditLogs', () => ({
    useAuditLogs: auditHookMocks.useAuditLogs,
    useAuditLog: auditHookMocks.useAuditLog,
}));

describe('audit pages', () => {
    beforeEach(() => {
        auditHookMocks.useAuditLogs.mockReset();
        auditHookMocks.useAuditLog.mockReset();
        setRouteParams({});
    });

    it('renders the audit log list and navigates to the selected entry', async () => {
        const user = userEvent.setup();
        auditHookMocks.useAuditLogs.mockReturnValue(createQueryResult(auditLogListResponse));

        render(<AuditLogListPage />);

        expect(screen.getByRole('heading', { name: 'Audit Logs' })).toBeInTheDocument();
        expect(screen.getByText('1 total entries')).toBeInTheDocument();
        expect(screen.getByText('USER_ROLE_UPDATED')).toBeInTheDocument();
        expect(screen.getByText('Admin User')).toBeInTheDocument();

        await user.click(screen.getByText('USER_ROLE_UPDATED'));
        expect(navigateMock).toHaveBeenLastCalledWith({
            to: '/audit-logs/$logId',
            params: { logId: auditLogListResponse.data[0].log_id },
        });
    });

    it('renders the audit log detail and returns to the list', async () => {
        const user = userEvent.setup();
        auditHookMocks.useAuditLog.mockReturnValue(createQueryResult(auditLogDetail));
        setRouteParams({ logId: auditLogDetail.log_id });

        render(<AuditLogDetailPage />);

        expect(screen.getByRole('heading', { name: 'Audit Log Detail' })).toBeInTheDocument();
        expect(screen.getByText('Event Details')).toBeInTheDocument();
        expect(screen.getByText('Detail JSON')).toBeInTheDocument();
        expect(screen.getByText('CASE_ASSIGNED')).toBeInTheDocument();

        await user.click(screen.getByRole('button', { name: 'Back to List' }));
        expect(navigateMock).toHaveBeenLastCalledWith({ to: '/audit-logs' });
    });
});
