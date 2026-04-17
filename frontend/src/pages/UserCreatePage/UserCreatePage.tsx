import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate } from '@tanstack/react-router';
import { useCreateUser } from '~/hooks/useUsers';
import { PageHeader } from '~/components/templates/PageHeader/PageHeader';
import { FormPageTemplate } from '~/components/templates/FormPageTemplate/FormPageTemplate';
import { Card } from '~/components/ui/Card/Card';
import { Input } from '~/components/ui/Input/Input';
import { Select } from '~/components/ui/Select/Select';
import { Button } from '~/components/ui/Button/Button';

const createUserSchema = z.object({
    username: z.string().min(3, 'Username must be at least 3 characters'),
    full_name: z.string().min(1, 'Full name is required'),
    email: z.string().email('Invalid email address'),
    password: z.string().min(8, 'Password must be at least 8 characters'),
    role: z.enum(['OPERATOR', 'REVIEWER', 'MANAGER']),
});

type CreateUserForm = z.infer<typeof createUserSchema>;

const roleOptions = [
    { label: 'Select role...', value: '' },
    { label: 'Operator', value: 'OPERATOR' },
    { label: 'Reviewer', value: 'REVIEWER' },
    { label: 'Manager', value: 'MANAGER' },
];

export function UserCreatePage() {
    const navigate = useNavigate();
    const createUser = useCreateUser();

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<CreateUserForm>({
        resolver: zodResolver(createUserSchema),
    });

    const onSubmit = (data: CreateUserForm) => {
        createUser.mutate(data, {
            onSuccess: (res) => {
                navigate({ to: '/users/$userId', params: { userId: res.user_id } });
            },
        });
    };

    return (
        <FormPageTemplate
            header={
                <PageHeader
                    title="Create User"
                    subtitle="Add a new user to the system"
                    actions={
                        <Button variant="ghost" onClick={() => navigate({ to: '/users' })}>
                            Cancel
                        </Button>
                    }
                />
            }
            form={
                <Card>
                    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <Input
                                label="Username"
                                error={errors.username?.message}
                                {...register('username')}
                            />
                            <Input
                                label="Full Name"
                                error={errors.full_name?.message}
                                {...register('full_name')}
                            />
                            <Input
                                label="Email"
                                type="email"
                                error={errors.email?.message}
                                {...register('email')}
                            />
                            <Input
                                label="Password"
                                type="password"
                                error={errors.password?.message}
                                {...register('password')}
                            />
                            <Select
                                label="Role"
                                options={roleOptions}
                                error={errors.role?.message}
                                {...register('role')}
                            />
                        </div>

                        {createUser.isError && (
                            <p className="text-xs text-[var(--color-status-danger)]">
                                Failed to create user. Please try again.
                            </p>
                        )}

                        <div className="flex justify-end">
                            <Button type="submit" loading={createUser.isPending}>
                                Create User
                            </Button>
                        </div>
                    </form>
                </Card>
            }
            footer={<div />}
        />
    );
}
