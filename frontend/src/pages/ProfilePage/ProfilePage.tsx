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
        current_password: z.string().min(1, 'Current password is required'),
        new_password: z.string().min(8, 'New password must be at least 8 characters'),
        confirm_password: z.string().min(1, 'Confirm password is required'),
    })
    .refine((d) => d.new_password === d.confirm_password, {
        message: 'Passwords do not match',
        path: ['confirm_password'],
    });

type ChangePasswordForm = z.infer<typeof changePasswordSchema>;

export function ProfilePage() {
    const user = useAuthStore((s) => s.user);
    const changePassword = useChangePassword();

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<ChangePasswordForm>({
        resolver: zodResolver(changePasswordSchema),
    });

    const onSubmit = (data: ChangePasswordForm) => {
        changePassword.mutate(data);
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
