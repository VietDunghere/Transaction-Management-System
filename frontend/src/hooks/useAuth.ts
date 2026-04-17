import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from '@tanstack/react-router';
import { authService } from '~/services/authService';
import { useAuthStore } from '~/stores/useAuthStore';
import { setAccessToken, setRefreshToken, clearTokens } from '~/utils/localStorage';
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
    });
}

export function useLogout() {
    const clearAuth = useAuthStore((s) => s.clearAuth);
    const queryClient = useQueryClient();
    const navigate = useNavigate();

    return useMutation({
        mutationFn: () => authService.logout(),
        onSettled: () => {
            clearTokens();
            clearAuth();
            queryClient.clear();
            navigate({ to: '/login' });
        },
    });
}

export function useChangePassword() {
    return useMutation({
        mutationFn: (data: ChangePasswordRequest) => authService.changePassword(data),
    });
}
