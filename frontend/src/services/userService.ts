import { apiClient } from './apiClient';
import type {
    User,
    CreateUserRequest,
    UpdateRoleRequest,
    UpdateRoleResponse,
    MessageResponse,
    PagedResponse,
} from '~/types/api';
import type { UserSearchParams } from '~/types/searchParams';

export const userService = {
    getUsers(params: UserSearchParams) {
        return apiClient.get<unknown, PagedResponse<User>>('/users', { params });
    },

    getUser(userId: string) {
        return apiClient.get<unknown, User>(`/users/${userId}`);
    },

    createUser(data: CreateUserRequest) {
        return apiClient.post<unknown, User>('/users', data);
    },

    disableUser(userId: string) {
        return apiClient.patch<unknown, MessageResponse>(`/users/${userId}/disable`);
    },

    enableUser(userId: string) {
        return apiClient.patch<unknown, MessageResponse>(`/users/${userId}/enable`);
    },

    updateUserRole(userId: string, data: UpdateRoleRequest) {
        return apiClient.patch<unknown, UpdateRoleResponse>(`/users/${userId}/role`, data);
    },
};
