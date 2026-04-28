import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { UserListPage } from '~/pages/UserListPage/UserListPage';
import { UserCreatePage } from '~/pages/UserCreatePage/UserCreatePage';
import { UserDetailPage } from '~/pages/UserDetailPage/UserDetailPage';
import { adminUser, operatorUser, userListResponse } from '~/test/fixtures';
import { createMutationResult, createQueryResult, navigateMock, setAuthUser, setRouteParams } from '~/test/testUtils';

const userHookMocks = vi.hoisted(() => ({
    useUsers: vi.fn(),
    useUser: vi.fn(),
    useCreateUser: vi.fn(),
    useDisableUser: vi.fn(),
    useEnableUser: vi.fn(),
    useUpdateUserRole: vi.fn(),
}));

vi.mock('~/hooks/useUsers', () => ({
    useUsers: userHookMocks.useUsers,
    useUser: userHookMocks.useUser,
    useCreateUser: userHookMocks.useCreateUser,
    useDisableUser: userHookMocks.useDisableUser,
    useEnableUser: userHookMocks.useEnableUser,
    useUpdateUserRole: userHookMocks.useUpdateUserRole,
}));

describe('user pages', () => {
    beforeEach(() => {
        userHookMocks.useUsers.mockReset();
        userHookMocks.useUser.mockReset();
        userHookMocks.useCreateUser.mockReset();
        userHookMocks.useDisableUser.mockReset();
        userHookMocks.useEnableUser.mockReset();
        userHookMocks.useUpdateUserRole.mockReset();
        setRouteParams({});
        setAuthUser(null);
    });

    it('renders the user list and exposes the admin action', async () => {
        const user = userEvent.setup();
        userHookMocks.useUsers.mockReturnValue(createQueryResult(userListResponse));
        setAuthUser(adminUser);

        render(<UserListPage />);

        expect(screen.getByRole('heading', { name: 'Users' })).toBeInTheDocument();
        expect(screen.getByText('Create User')).toBeInTheDocument();
        expect(screen.getByText('operator')).toBeInTheDocument();
        expect(screen.getByText('reviewer')).toBeInTheDocument();

        await user.click(screen.getByText('operator'));
        expect(navigateMock).toHaveBeenLastCalledWith({
            to: '/users/$userId',
            params: { userId: operatorUser.user_id },
        });
    });

    it('creates a user and navigates to the new profile', async () => {
        const user = userEvent.setup();
        const createUserMutation = createMutationResult({ data: { user_id: 'user-new' } });
        userHookMocks.useCreateUser.mockReturnValue(createUserMutation);

        render(<UserCreatePage />);

        await user.type(screen.getByLabelText('Username'), 'new.user');
        await user.type(screen.getByLabelText('Full Name'), 'New User');
        await user.type(screen.getByLabelText('Email'), 'new.user@example.com');
        await user.type(screen.getByLabelText('Password'), 'Secret123!');
        await user.selectOptions(screen.getByLabelText('Role'), 'REVIEWER');
        await user.click(screen.getByRole('button', { name: 'Create User' }));

        expect(createUserMutation.mutate).toHaveBeenCalledWith(
            {
                username: 'new.user',
                full_name: 'New User',
                email: 'new.user@example.com',
                password: 'Secret123!',
                role: 'REVIEWER',
            },
            expect.any(Object),
        );
        expect(navigateMock).toHaveBeenLastCalledWith({
            to: '/users/$userId',
            params: { userId: 'user-new' },
        });
    });

    it('shows user details and opens the role modal', async () => {
        const user = userEvent.setup();
        userHookMocks.useUser.mockReturnValue(createQueryResult(operatorUser));
        userHookMocks.useDisableUser.mockReturnValue(createMutationResult());
        userHookMocks.useEnableUser.mockReturnValue(createMutationResult());
        const updateRoleMutation = createMutationResult({ data: { role: 'REVIEWER' } });
        userHookMocks.useUpdateUserRole.mockReturnValue(updateRoleMutation);
        setAuthUser(adminUser);
        setRouteParams({ userId: operatorUser.user_id });

        render(<UserDetailPage />);

        expect(screen.getByRole('heading', { name: operatorUser.full_name })).toBeInTheDocument();
        expect(screen.getByText('User Details')).toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'Disable' })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'Change Role' })).toBeInTheDocument();

        await user.click(screen.getByRole('button', { name: 'Change Role' }));
        expect(screen.getByText('Change User Role')).toBeInTheDocument();
        await user.selectOptions(screen.getByLabelText('New Role'), 'REVIEWER');
        await user.click(screen.getByRole('button', { name: 'Update Role' }));

        expect(updateRoleMutation.mutate).toHaveBeenCalledWith(
            { userId: operatorUser.user_id, role: 'REVIEWER' },
            expect.any(Object),
        );
    });
});
