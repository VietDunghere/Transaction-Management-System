import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Navigate } from '@tanstack/react-router';
import { useLogin } from '~/hooks/useAuth';
import { useAuthStore } from '~/stores/useAuthStore';
import { useUIStore } from '~/stores/useUIStore';
import { Button } from '~/components/ui/Button/Button';
import { Input } from '~/components/ui/Input/Input';
import { Sun, Moon } from 'lucide-react';
import { GeometricBackground } from './GeometricBackground';
import { CosmicBackground } from './CosmicBackground';
import iconLogo from '~/assets/icon.png';

const loginSchema = z.object({
    username: z.string().min(1, 'Username is required'),
    password: z.string().min(1, 'Password is required'),
});

type LoginForm = z.infer<typeof loginSchema>;

export function LoginPage() {
    const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
    const login = useLogin();
    const { theme, toggleTheme } = useUIStore();

    const [mountedLight, setMountedLight] = useState(theme === 'light');
    const [mountedDark, setMountedDark] = useState(theme === 'dark');
    useEffect(() => {
        if (theme === 'light') setMountedLight(true);
        else setMountedDark(true);
    }, [theme]);

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
        <div className="relative h-screen w-full overflow-hidden flex items-center justify-center">
            {/* Full-page animated background — crossfade between geometric (light) and cosmic (dark) */}
            <div className="fixed inset-0 z-0">
                {mountedLight && (
                    <div style={{ display: theme === 'light' ? 'block' : 'none' }}>
                        <GeometricBackground />
                    </div>
                )}
                {mountedDark && (
                    <div style={{ display: theme === 'dark' ? 'block' : 'none' }}>
                        <CosmicBackground />
                    </div>
                )}
            </div>

            <div className="w-full max-w-300 mx-auto p-4 md:p-6 relative z-10">
                <div className="rounded-[26px]">
                    {/* The main card */}
                    <div
                        className={`flex flex-col md:flex-row rounded-[24px] overflow-hidden max-h-[calc(100vh-3rem)] relative animate-in fade-in zoom-in-95 duration-200 ${theme === 'dark' ? 'bg-transparent' : 'backdrop-blur-xs shadow-2xl bg-white/10 shadow-black/10'}`}
                    >
                        {/* Theme Toggle Icon Button - Placed at bottom right of the card, visible on both Mobile and Desktop */}
                        <button
                            onClick={toggleTheme}
                            className="absolute bottom-3 right-3 md:bottom-5 md:right-5 z-50 flex size-8 md:size-11 items-center justify-center rounded-full bg-text-primary/10 md:bg-white/10 hover:bg-text-primary/20 md:hover:bg-white/20 backdrop-blur-xl border border-border-default md:border-white/20 text-text-primary md:text-white shadow-xl transition-all duration-300 cursor-pointer focus:outline-none hover:scale-110 active:scale-95"
                            aria-label="Toggle theme"
                        >
                            {theme === 'light' ? (
                                <Moon className="size-3.5 md:size-[1.15rem] animate-in fade-in zoom-in duration-300" />
                            ) : (
                                <Sun className="size-3.5 md:size-[1.15rem] animate-in fade-in zoom-in duration-300" />
                            )}
                        </button>

                        {/* Left: Login Form */}
                        <div className="w-full md:w-1/2 p-6 md:p-10 lg:p-14 flex flex-col justify-center items-center relative overflow-y-auto">
                            <div className="w-full max-w-md relative z-10">
                                <div className="text-center mb-6">
                                    <div className="flex items-center justify-center gap-3 mb-4">
                                        <img src={iconLogo} alt="HuzaFraud" className="size-10" />
                                        <span className="text-2xl font-bold tracking-tight text-text-primary">
                                            HuzaFraud
                                        </span>
                                    </div>
                                    <h1 className="text-3xl font-bold text-text-primary mb-2 tracking-tight">
                                        Login To Your Account
                                    </h1>
                                    <p className="text-base text-text-secondary">
                                        Enter your username and password to login
                                    </p>
                                </div>

                                <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
                                    <Input
                                        inputSize="lg"
                                        className="border-2 bg-transparent"
                                        label="Username"
                                        placeholder="Enter your username"
                                        error={errors.username?.message}
                                        {...register('username')}
                                    />

                                    <div>
                                        <Input
                                            inputSize="lg"
                                            className="border-2 bg-transparent"
                                            label="Password"
                                            type="password"
                                            placeholder="Enter your password"
                                            error={errors.password?.message}
                                            {...register('password')}
                                        />
                                        <div className="w-full flex justify-start mt-2">
                                            <button
                                                type="button"
                                                className="text-sm font-medium text-text-primary hover:text-status-info hover:underline"
                                            >
                                                Forgot password?
                                            </button>
                                        </div>
                                    </div>

                                    {login.isError && (
                                        <p className="text-sm text-status-danger text-center bg-feedback-danger-bg p-3 rounded-lg border border-status-danger/20">
                                            {(login.error as { response?: { data?: { message?: string } } })?.response
                                                ?.data?.message ?? 'Login failed. Please try again.'}
                                        </p>
                                    )}

                                    <Button
                                        type="submit"
                                        variant="primary"
                                        loading={login.isPending}
                                        className="w-full mt-2 py-3 text-base rounded-xl shadow-md transition-all duration-100 ease-out hover:scale-105 hover:shadow-xl active:scale-95"
                                    >
                                        Login
                                    </Button>
                                </form>
                            </div>
                        </div>

                        {/* Right: Abstract Graphic/Image */}
                        <div className="hidden md:block w-full md:w-1/2 relative bg-black">
                            <img
                                src="/login_side_image.png"
                                alt="Security and Analytics"
                                className="absolute inset-0 w-full h-full object-cover mix-blend-luminosity opacity-80"
                            />
                            <div className="absolute inset-0"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
