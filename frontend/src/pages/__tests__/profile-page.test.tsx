import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { ProfilePage } from '~/pages/ProfilePage/ProfilePage';
import { adminUser } from '~/test/fixtures';
import { createMutationResult, setAuthUser } from '~/test/testUtils';

const authHookMocks = vi.hoisted(() => ({
    useChangePassword: vi.fn(),
}));

vi.mock('~/hooks/useAuth', () => ({
    useChangePassword: authHookMocks.useChangePassword,
}));

describe('profile page', () => {
    beforeEach(() => {
        authHookMocks.useChangePassword.mockReset();
        setAuthUser(adminUser);
    });

    it('renders the current user and submits a password change', async () => {
        const user = userEvent.setup();
        const changePasswordMutation = createMutationResult();
        authHookMocks.useChangePassword.mockReturnValue(changePasswordMutation);

        render(<ProfilePage />);

        expect(screen.getByRole('heading', { name: 'Profile' })).toBeInTheDocument();
        expect(screen.getByText('Account Information')).toBeInTheDocument();
        expect(screen.getByText(adminUser.username)).toBeInTheDocument();
        expect(screen.getByText(adminUser.full_name)).toBeInTheDocument();
        expect(screen.getByText(adminUser.role)).toBeInTheDocument();

        await user.type(screen.getByLabelText('Current Password'), 'OldSecret123');
        await user.type(screen.getByLabelText('New Password'), 'NewSecret123');
        await user.type(screen.getByLabelText('Confirm New Password'), 'NewSecret123');
        await user.click(screen.getByRole('button', { name: 'Update Password' }));

        expect(changePasswordMutation.mutate).toHaveBeenCalledWith(
            {
                current_password: 'OldSecret123',
                new_password: 'NewSecret123',
                confirm_password: 'NewSecret123',
            },
            expect.any(Object),
        );
    });
});
