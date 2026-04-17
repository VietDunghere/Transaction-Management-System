import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Navigate } from '@tanstack/react-router';
import { useLogin } from '~/hooks/useAuth';
import { useAuthStore } from '~/stores/useAuthStore';
import { Button } from '~/components/ui/Button/Button';
import { Input } from '~/components/ui/Input/Input';

const loginSchema = z.object({
    username: z.string().min(1, 'Username is required'),
    password: z.string().min(1, 'Password is required'),
});

type LoginForm = z.infer<typeof loginSchema>;

export function LoginPage() {
    const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
    const login = useLogin();

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<LoginForm>({
        resolver: zodResolver(loginSchema),
    });

    if (isAuthenticated) {
        return <Navigate to="/" />;
    }

    const onSubmit = (data: LoginForm) => {
        login.mutate(data);
    };

    return (
        <div className="w-full max-w-md">
            <div className="bg-primary border border-[var(--color-border-default)] rounded-md p-8">
                <div className="text-center mb-8">
                    <div className="flex items-center justify-center gap-2 mb-4">
                        <div className="flex size-8 items-center justify-center rounded-sm bg-accent-indigo">
                            <span className="text-sm font-semibold text-white">H</span>
                        </div>
                        <span className="text-lg font-semibold text-[var(--color-text-primary)]">HuzaFraud</span>
                    </div>
                    <p className="text-sm text-[var(--color-text-secondary)]">Transaction Management System</p>
                </div>

                <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
                    <Input
                        label="Username"
                        placeholder="Enter your username"
                        error={errors.username?.message}
                        {...register('username')}
                    />
                    <Input
                        label="Password"
                        type="password"
                        placeholder="Enter your password"
                        error={errors.password?.message}
                        {...register('password')}
                    />

                    {login.isError && (
                        <p className="text-xs text-[var(--color-status-danger)]">
                            {(login.error as { response?: { data?: { message?: string } } })?.response?.data?.message ??
                                'Login failed. Please try again.'}
                        </p>
                    )}

                    <Button type="submit" loading={login.isPending} className="w-full mt-2">
                        Sign In
                    </Button>
                </form>
            </div>
        </div>
    );
}
