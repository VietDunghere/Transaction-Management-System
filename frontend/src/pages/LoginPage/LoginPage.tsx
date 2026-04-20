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

const loginSchema = z.object({
    username: z.string().min(1, 'Username is required'),
    password: z.string().min(1, 'Password is required'),
});

type LoginForm = z.infer<typeof loginSchema>;

export function LoginPage() {
    const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
    const login = useLogin();
    const { theme, toggleTheme } = useUIStore();

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
        <div className="w-full max-w-[1200px] mx-auto p-4 md:p-8">
            {/* The gradient frame - exceptionally thin to look like a premium glowing border */}
            <div className="bg-gradient-to-br from-[#fde047] via-[#4ade80] to-[#0ea5e9] p-[2px] rounded-[26px] sun-shadow transition-all duration-700 ease-in-out">
                
                {/* The main card - explicitly relative so the absolute button aligns to it globally */}
                <div className="flex flex-col md:flex-row bg-primary rounded-[24px] overflow-hidden min-h-[650px] transition-colors duration-700 ease-in-out relative">
                    
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
                    <div className="w-full md:w-1/2 p-10 md:p-16 lg:p-20 flex flex-col justify-center items-center relative transition-colors duration-700 ease-in-out">

                        <div className="w-full max-w-md relative z-10">
                            <div className="text-center mb-10">
                                <div className="flex justify-center mb-6">
                                    <div className="flex px-4 py-2 items-center justify-center rounded-lg bg-text-primary shadow-lg border border-border-default transition-colors duration-700 ease-in-out">
                                        <span className="text-xl font-bold tracking-widest text-bg-primary transition-colors duration-700 ease-in-out">HF-TMS</span>
                                    </div>
                                </div>
                                <h1 className="text-3xl font-bold text-text-primary mb-2 tracking-tight transition-colors duration-700 ease-in-out">Login To Your Account</h1>
                                <p className="text-base text-text-secondary transition-colors duration-700 ease-in-out">Enter your username and password to login</p>
                            </div>

                            <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-6">
                                <div>
                                    <Input
                                        className="py-6 text-base transition-colors duration-700 ease-in-out"
                                        label="Username"
                                        placeholder="Enter your username"
                                        error={errors.username?.message}
                                        {...register('username')}
                                    />
                                </div>
                                
                                <div>
                                    <Input
                                        className="py-6 text-base transition-colors duration-700 ease-in-out"
                                        label="Password"
                                        type="password"
                                        placeholder="Enter your password"
                                        error={errors.password?.message}
                                        {...register('password')}
                                    />
                                    <div className="w-full flex justify-start mt-2">
                                        <button type="button" className="text-sm font-medium text-text-primary hover:text-status-info transition-colors duration-700 ease-in-out hover:underline">
                                            Forgot password?
                                        </button>
                                    </div>
                                </div>

                                {login.isError && (
                                    <p className="text-sm text-status-danger text-center bg-feedback-danger-bg p-3 rounded-lg border border-status-danger/20 transition-colors duration-700 ease-in-out">
                                        {(login.error as { response?: { data?: { message?: string } } })?.response?.data?.message ??
                                            'Login failed. Please try again.'}
                                    </p>
                                )}

                                <Button 
                                    type="submit" 
                                    variant="primary"
                                    loading={login.isPending} 
                                    className="w-full mt-4 py-6 text-base rounded-xl shadow-md transition-all duration-300 ease-out hover:scale-105 hover:shadow-xl active:scale-95"
                                >
                                    Login
                                </Button>
                                
                                <div className="mt-8 flex items-center justify-center gap-3">
                                    <div className="h-px bg-border-default flex-1 transition-colors duration-700 ease-in-out"></div>
                                    <span className="text-xs text-text-primary px-2 uppercase tracking-widest font-bold transition-colors duration-700 ease-in-out">Secure Authentication</span>
                                    <div className="h-px bg-border-default flex-1 transition-colors duration-700 ease-in-out"></div>
                                </div>
                            </form>
                        </div>

                    </div>

                    {/* Right: Abstract Graphic/Image */}
                    <div className="hidden md:block w-full md:w-1/2 relative bg-black">
                        <img 
                            src="/login_side_image.png" 
                            alt="Security and Analytics" 
                            className="absolute inset-0 w-full h-full object-cover mix-blend-luminosity opacity-80 transition-opacity duration-700 ease-in-out"
                        />
                        <div className="absolute inset-0 bg-gradient-to-br from-black/80 via-transparent to-[#0f172a]/90 mix-blend-multiply transition-colors duration-700 ease-in-out"></div>
                    </div>

                </div>
            </div>
        </div>
    );
}
