import { apiClient } from './apiClient';
import type {
    LoginRequest,
    LoginResponse,
    MeResponse,
    RefreshResponse,
    ChangePasswordRequest,
    MessageResponse,
} from '~/types/api';

export const authService = {
    login(data: LoginRequest) {
        return apiClient.post<unknown, LoginResponse>('/auth/login', data);
    },

    logout() {
        return apiClient.post<unknown, MessageResponse>('/auth/logout');
    },

    getMe() {
        return apiClient.get<unknown, MeResponse>('/auth/me');
    },

    changePassword(data: ChangePasswordRequest) {
        return apiClient.patch<unknown, MessageResponse>('/auth/change-password', data);
    },

    refresh(refreshToken: string) {
        return apiClient.post<unknown, RefreshResponse>('/auth/refresh', {
            refresh_token: refreshToken,
        });
    },
};
