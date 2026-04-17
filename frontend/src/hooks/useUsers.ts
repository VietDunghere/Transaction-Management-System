import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { userService } from '~/services/userService';
import type { UserSearchParams } from '~/types/searchParams';
import type { CreateUserRequest, UpdateRoleRequest, Role } from '~/types/api';

export const userKeys = {
    all: ['users'] as const,
    list: (params: UserSearchParams) => ['users', 'list', params] as const,
    detail: (userId: string) => ['users', 'detail', userId] as const,
};

export function useUsers(params: UserSearchParams) {
    return useQuery({
        queryKey: userKeys.list(params),
        queryFn: () => userService.getUsers(params),
    });
}

export function useUser(userId: string) {
    return useQuery({
        queryKey: userKeys.detail(userId),
        queryFn: () => userService.getUser(userId),
        enabled: !!userId,
    });
}

export function useCreateUser() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (data: CreateUserRequest) => userService.createUser(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: userKeys.all });
        },
    });
}

export function useDisableUser() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (userId: string) => userService.disableUser(userId),
        onSuccess: (_data, userId) => {
            queryClient.invalidateQueries({ queryKey: userKeys.detail(userId) });
            queryClient.invalidateQueries({ queryKey: userKeys.all });
        },
    });
}

export function useEnableUser() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (userId: string) => userService.enableUser(userId),
        onSuccess: (_data, userId) => {
            queryClient.invalidateQueries({ queryKey: userKeys.detail(userId) });
            queryClient.invalidateQueries({ queryKey: userKeys.all });
        },
    });
}

export function useUpdateUserRole() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ userId, role }: { userId: string; role: Exclude<Role, 'ADMIN'> }) =>
            userService.updateUserRole(userId, { role } as UpdateRoleRequest),
        onSuccess: (_data, vars) => {
            queryClient.invalidateQueries({ queryKey: userKeys.detail(vars.userId) });
            queryClient.invalidateQueries({ queryKey: userKeys.all });
        },
    });
}
