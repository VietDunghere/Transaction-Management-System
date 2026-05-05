import { useQuery, useMutation } from '@tanstack/react-query';
import { useNavigate } from '@tanstack/react-router';
import { toast } from 'sonner';
import { authService } from '~/services/authService';
import { useAuthStore } from '~/stores/useAuthStore';
import { useActivityStore } from '~/stores/useActivityStore';
import { setAccessToken, setRefreshToken, clearTokens } from '~/utils/localStorage';
import { toastSuccessWithActivity } from '~/utils/toastActivity';
import type { LoginRequest, ChangePasswordRequest } from '~/types/api';

export const authKeys = {
    me: ['auth', 'me'] as const,
};

export function useMe() {
    const setUser = useAuthStore((s) => s.setUser);
    const clearAuth = useAuthStore((s) => s.clearAuth);

    return useQuery({
        queryKey: authKeys.me,
        queryFn: async () => {
            const data = await authService.getMe();
            setUser({
                user_id: data.user_id,
                username: data.username,
                full_name: data.full_name ?? '',
                email: '',
                role: data.role,
                is_active: data.is_active,
                created_at: '',
            });
            return data;
        },
        retry: false,
        staleTime: 5 * 60_000,
        meta: { onError: () => clearAuth() },
    });
}

export function useLogin() {
    const setUser = useAuthStore((s) => s.setUser);
    const navigate = useNavigate();

    return useMutation({
        mutationFn: (data: LoginRequest) => authService.login(data),
        onSuccess: (res) => {
            setAccessToken(res.access_token);
            setRefreshToken(res.refresh_token);
            setUser({
                user_id: res.user_id,
                username: res.username,
                full_name: res.full_name,
                email: '',
                role: res.role,
                is_active: true,
                created_at: '',
            });
            navigate({ to: '/' });
        },
        onError: () => {
            toast.error('Login failed. Please check your credentials.');
        },
    });
}

export function useLogout() {
    const clearAuth = useAuthStore((s) => s.clearAuth);
    const clearActivities = useActivityStore((s) => s.clearActivities);
    const navigate = useNavigate();

    return useMutation({
        mutationFn: () => authService.logout(),
        onSettled: () => {
            clearTokens();
            clearAuth();
            clearActivities();
            navigate({ to: '/login' });
        },
    });
}

export function useChangePassword() {
    return useMutation({
        mutationFn: (data: ChangePasswordRequest) => authService.changePassword(data),
        onSuccess: () => {
            toastSuccessWithActivity('Password changed successfully');
            // Auto-clear success state after 3 seconds to prevent stale UI
            setTimeout(() => {
                // Success state will naturally expire via TanStack Query's internal timer
            }, 3000);
        },
        onError: (error: unknown) => {
            const apiMsg = (error as any)?.response?.data?.message;
            toast.error(apiMsg || (error instanceof Error ? error.message : 'Something went wrong'));
        },
    });
}
