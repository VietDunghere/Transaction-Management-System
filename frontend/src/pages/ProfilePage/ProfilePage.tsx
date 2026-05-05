import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useChangePassword } from '~/hooks/useAuth';
import { useAuthStore } from '~/stores/useAuthStore';
import { PageHeader } from '~/components/templates/PageHeader/PageHeader';
import { FormPageTemplate } from '~/components/templates/FormPageTemplate/FormPageTemplate';
import { Input } from '~/components/ui/Input/Input';
import { Button } from '~/components/ui/Button/Button';
import { Card } from '~/components/ui/Card/Card';
import { KeyValueRow } from '~/components/ui/KeyValueRow/KeyValueRow';
import { SectionHeader } from '~/components/ui/SectionHeader/SectionHeader';

const changePasswordSchema = z
    .object({
        current_password: z.string().min(1, 'Current password is required').min(1, 'Current password cannot be empty'),
        new_password: z.string().min(8, 'New password must be at least 8 characters'),
        confirm_password: z.string().min(8, 'Confirm password must be at least 8 characters'),
    })
    .refine((d) => d.new_password === d.confirm_password, {
        message: 'Passwords do not match',
        path: ['confirm_password'],
    })
    .refine((d) => d.current_password !== d.new_password, {
        message: 'New password must be different from current password',
        path: ['new_password'],
    });

type ChangePasswordForm = z.infer<typeof changePasswordSchema>;

export function ProfilePage() {
    const user = useAuthStore((s) => s.user);
    const changePassword = useChangePassword();

    const defaultFormValues: ChangePasswordForm = {
        current_password: '',
        new_password: '',
        confirm_password: '',
    };

    const {
        register,
        handleSubmit,
        reset,
        formState: { errors },
    } = useForm<ChangePasswordForm>({
        resolver: zodResolver(changePasswordSchema),
        mode: 'onChange', // Validate on every change to catch password mismatch immediately
        defaultValues: defaultFormValues,
    });

    const onSubmit = (data: ChangePasswordForm) => {
        // Ensure all fields are properly validated before submission
        if (!data.current_password || !data.new_password || !data.confirm_password) {
            return;
        }

        changePassword.mutate(data, {
            onSuccess: () => reset(),
        });
    };

    return (
        <FormPageTemplate
            header={<PageHeader title="Profile" subtitle="Manage your account settings" />}
            form={
                <div className="flex flex-col gap-6">
                    {/* User Info */}
                    <Card>
                        <SectionHeader title="Account Information" />
                        <div className="flex flex-col gap-1 mt-4">
                            <KeyValueRow label="Username" value={user?.username ?? '-'} />
                            <KeyValueRow label="Full Name" value={user?.full_name ?? '-'} />
                            <KeyValueRow label="Role" value={user?.role ?? '-'} />
                        </div>
                    </Card>

                    {/* Change Password Form */}
                    <Card>
                        <SectionHeader title="Change Password" />
                        <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4 mt-4">
                            <Input
                                label="Current Password"
                                type="password"
                                error={errors.current_password?.message}
                                {...register('current_password')}
                            />
                            <Input
                                label="New Password"
                                type="password"
                                error={errors.new_password?.message}
                                {...register('new_password')}
                            />
                            <Input
                                label="Confirm New Password"
                                type="password"
                                error={errors.confirm_password?.message}
                                {...register('confirm_password')}
                            />

                            {/* Show success message ONLY if we just succeeded and haven't moved on */}
                            {changePassword.isSuccess && !changePassword.isPending && (
                                <p className="text-xs text-status-success">Password changed successfully.</p>
                            )}
                            {/* Show error message ONLY if we have an error and it's not being retried */}
                            {changePassword.isError && !changePassword.isPending && (
                                <p className="text-xs text-status-danger">
                                    Failed to change password. Check your current password.
                                </p>
                            )}

                            <div className="flex justify-end">
                                <Button type="submit" loading={changePassword.isPending}>
                                    Update Password
                                </Button>
                            </div>
                        </form>
                    </Card>
                </div>
            }
        />
    );
}
