import { useEffect, useRef, useState } from 'react';
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
import { GeometricBackground, type GeometricBackgroundHandle } from './GeometricBackground';
import { CosmicBackground } from './CosmicBackground';
import iconLogo from '~/assets/icon.png';

type SidePanel = 'light-img' | 'dark-img' | 'dark-video' | 'light-video';

const TRANSITION_MS = 500;
const BG_FADE_MS = 1000;
const VIDEO_BG_LEAD_S = 0.8; // bg fires this many seconds before video ends

const loginSchema = z.object({
    username: z.string().min(1, 'Username is required'),
    password: z.string().min(1, 'Password is required'),
});

type LoginForm = z.infer<typeof loginSchema>;

export function LoginPage() {
    const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
    const login = useLogin();
    const { theme, toggleTheme } = useUIStore();

    const geometricRef = useRef<GeometricBackgroundHandle>(null);
    const [isTransitioning, setIsTransitioning] = useState(false);
    const transitionTimeoutRef = useRef<number | null>(null);
    const sidePanelTimeoutRef = useRef<number | null>(null);

    // Special flow: 50% chance per mount — stable for the entire session
    const isSpecialFlow = useRef(Math.random() < 0.5);
    const [sidePanel, setSidePanel] = useState<SidePanel>(() =>
        isSpecialFlow.current && theme === 'light' ? 'light-img' : 'dark-img',
    );

    // Video refs — elements stay mounted for preloading; driven imperatively
    const darkVideoRef = useRef<HTMLVideoElement>(null);
    const lightVideoRef = useRef<HTMLVideoElement>(null);

    // True only between play() and onEnded/pause — used to collapse the
    // protective source image the moment the video has its first frame,
    // so it is already gone before onEnded fires (no end-of-video flash).
    const [darkVideoPlaying, setDarkVideoPlaying] = useState(false);
    const [lightVideoPlaying, setLightVideoPlaying] = useState(false);

    useEffect(() => {
        const dv = darkVideoRef.current;
        const lv = lightVideoRef.current;
        if (sidePanel === 'dark-video') {
            lv?.pause();
            setLightVideoPlaying(false);
            if (dv) {
                dv.currentTime = 0;
                void dv.play();
            }
        } else if (sidePanel === 'light-video') {
            dv?.pause();
            setDarkVideoPlaying(false);
            if (lv) {
                lv.currentTime = 0;
                void lv.play();
            }
        } else {
            dv?.pause();
            lv?.pause();
            setDarkVideoPlaying(false);
            setLightVideoPlaying(false);
        }
    }, [sidePanel]);

    const [mountedLight, setMountedLight] = useState(theme === 'light');
    const [mountedDark, setMountedDark] = useState(theme === 'dark');
    useEffect(() => {
        if (theme === 'light') setMountedLight(true);
        else setMountedDark(true);
    }, [theme]);

    // Edge case 3: cleanup timeouts on unmount
    useEffect(() => {
        return () => {
            if (transitionTimeoutRef.current) clearTimeout(transitionTimeoutRef.current);
            if (sidePanelTimeoutRef.current) clearTimeout(sidePanelTimeoutRef.current);
        };
    }, []);

    // Extracted so they can be called from handleToggleTheme (normal flow)
    // and from onPlay (special flow — scheduled at duration - VIDEO_BG_LEAD_S).
    const startBgToDark = () => {
        geometricRef.current?.implode();
        transitionTimeoutRef.current = window.setTimeout(() => {
            setMountedDark(true);
            toggleTheme();
            transitionTimeoutRef.current = window.setTimeout(() => {
                setIsTransitioning(false);
                transitionTimeoutRef.current = null;
            }, BG_FADE_MS);
        }, TRANSITION_MS - 200);
    };

    const startBgToLight = () => {
        setMountedLight(true);
        toggleTheme();
        transitionTimeoutRef.current = window.setTimeout(() => {
            requestAnimationFrame(() => {
                geometricRef.current?.explode(() => {
                    setIsTransitioning(false);
                    transitionTimeoutRef.current = null;
                });
            });
        }, TRANSITION_MS - 200);
    };

    const handleToggleTheme = () => {
        if (isTransitioning || darkVideoPlaying || lightVideoPlaying) return;

        setIsTransitioning(true);

        if (theme === 'light') {
            if (isSpecialFlow.current) {
                // Video fires immediately; bg is scheduled from onPlay
                // once we know the exact duration.
                setSidePanel('dark-video');
            } else {
                startBgToDark();
            }
        } else {
            if (isSpecialFlow.current) {
                setSidePanel('light-video');
            } else {
                startBgToLight();
            }
        }
    };

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
            {/* Background layers: color layers crossfade, particles are a separate non-fading layer */}
            <div className="fixed inset-0 z-0" style={{ background: '#000' }}>
                {/* Light bg color — fades */}
                {mountedLight && (
                    <div
                        style={{
                            position: 'absolute',
                            inset: 0,
                            backgroundColor: '#E4EAF1',
                            opacity: theme === 'light' ? 1 : 0,
                            transition: `opacity ${BG_FADE_MS}ms ease`,
                        }}
                    />
                )}
                {/* Dark bg (cosmic) — fades */}
                {mountedDark && (
                    <div
                        style={{
                            position: 'absolute',
                            inset: 0,
                            opacity: theme === 'dark' ? 1 : 0,
                            transition: `opacity ${BG_FADE_MS}ms ease`,
                            pointerEvents: theme === 'dark' ? 'auto' : 'none',
                        }}
                    >
                        <CosmicBackground />
                    </div>
                )}
                {/* Light particles — separate layer, never faded by wrapper */}
                {mountedLight && (
                    <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }}>
                        <GeometricBackground ref={geometricRef} />
                    </div>
                )}
            </div>

            <div className="w-full max-w-300 mx-auto p-4 md:p-6 relative z-10">
                <div className="rounded-[26px]">
                    {/* The main card */}
                    <div
                        className={`flex flex-col md:flex-row rounded-[24px] overflow-hidden max-h-[calc(100vh-3rem)] relative animate-in fade-in zoom-in-95 duration-200 ${theme === 'dark' ? 'bg-transparent' : 'backdrop-blur-sm shadow-2xl bg-white/10 shadow-black/10'}`}
                    >
                        {/* Theme Toggle Icon Button - Placed at bottom right of the card, visible on both Mobile and Desktop */}
                        <button
                            onClick={handleToggleTheme}
                            disabled={isTransitioning || darkVideoPlaying || lightVideoPlaying}
                            className={`absolute bottom-3 right-3 md:bottom-5 md:right-5 z-50 flex size-8 md:size-11 items-center justify-center rounded-full bg-text-primary/10 md:bg-white/10 hover:bg-text-primary/20 md:hover:bg-white/20 backdrop-blur-xl border border-border-default md:border-white/20 text-text-primary md:text-white shadow-xl transition-all duration-300 focus:outline-none hover:scale-110 active:scale-95 ${isTransitioning || darkVideoPlaying || lightVideoPlaying ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
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
                        <div className="hidden md:block w-full md:w-1/2 relative bg-black overflow-hidden">
                            {isSpecialFlow.current ? (
                                <>
                                    {/*
                                     * Layer 1 (bottom): dark image — always painted.
                                     * Already decoded before the video ends, so no
                                     * loading gap when revealing it.
                                     */}
                                    <img
                                        className="absolute inset-0 w-full h-full object-cover"
                                        src="/login_side_image.png"
                                        alt=""
                                    />
                                    {/*
                                     * Layer 2: light image — sits on top of dark image.
                                     * Visible only during light-facing states; fades out
                                     * to reveal the dark image already painted below.
                                     */}
                                    {/*
                                     * Layer 2: light image — only shown before the dark
                                     * video fires onPlay (buffer guard). Hidden instantly
                                     * once the video has its first frame, so it is
                                     * already gone long before onEnded fires.
                                     */}
                                    <img
                                        className="absolute inset-0 w-full h-full object-cover"
                                        style={{
                                            opacity:
                                                sidePanel === 'light-img' ||
                                                (sidePanel === 'dark-video' && !darkVideoPlaying)
                                                    ? 1
                                                    : 0,
                                        }}
                                        src="/login_side_image_1.png"
                                        alt=""
                                    />
                                    {/*
                                     * Layers 3 & 4: videos — always mounted for preload,
                                     * driven imperatively. Never remounted.
                                     */}
                                    <video
                                        ref={darkVideoRef}
                                        className="absolute inset-0 w-full h-full object-cover"
                                        style={{ opacity: sidePanel === 'dark-video' ? 1 : 0 }}
                                        src="/login_toggle_dark.mp4"
                                        preload="auto"
                                        muted
                                        playsInline
                                        onPlay={() => {
                                            setDarkVideoPlaying(true);
                                            const dur = darkVideoRef.current?.duration;
                                            const delay = isFinite(dur!)
                                                ? Math.max(0, (dur! - VIDEO_BG_LEAD_S) * 1000)
                                                : 2000;
                                            sidePanelTimeoutRef.current = window.setTimeout(startBgToDark, delay);
                                        }}
                                        onEnded={() => {
                                            setDarkVideoPlaying(false);
                                            setSidePanel('dark-img');
                                        }}
                                    />
                                    <video
                                        ref={lightVideoRef}
                                        className="absolute inset-0 w-full h-full object-cover"
                                        style={{ opacity: sidePanel === 'light-video' ? 1 : 0 }}
                                        src="/login_toggle_light.mp4"
                                        preload="auto"
                                        muted
                                        playsInline
                                        onPlay={() => {
                                            setLightVideoPlaying(true);
                                            const dur = lightVideoRef.current?.duration;
                                            const delay = isFinite(dur!)
                                                ? Math.max(0, (dur! - VIDEO_BG_LEAD_S) * 1000)
                                                : 2000;
                                            sidePanelTimeoutRef.current = window.setTimeout(startBgToLight, delay);
                                        }}
                                        onEnded={() => {
                                            setLightVideoPlaying(false);
                                            setSidePanel('light-img');
                                        }}
                                    />
                                </>
                            ) : (
                                <img
                                    src="/login_side_image.png"
                                    alt="Security and Analytics"
                                    className="absolute inset-0 w-full h-full object-cover"
                                />
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
