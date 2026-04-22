import { useState } from 'react';
import { useNavigate } from '@tanstack/react-router';
import { useUsers } from '~/hooks/useUsers';
import { useAuthStore } from '~/stores/useAuthStore';
import type { UserSearchParams } from '~/types/searchParams';
import type { Role } from '~/types/api';
import { PageHeader } from '~/components/templates/PageHeader/PageHeader';
import { ListPageTemplate } from '~/components/templates/ListPageTemplate/ListPageTemplate';
import { TableShell } from '~/components/ui/TableShell/TableShell';
import { FilterBar } from '~/components/ui/FilterBar/FilterBar';
import { Select } from '~/components/ui/Select/Select';
import { Pagination } from '~/components/ui/Pagination/Pagination';
import { Badge } from '~/components/ui/Badge/Badge';
import { Button } from '~/components/ui/Button/Button';
import { LoadingSkeleton } from '~/components/ui/LoadingSkeleton/LoadingSkeleton';
import { ErrorState } from '~/components/ui/ErrorState/ErrorState';
import { EmptyState } from '~/components/ui/EmptyState/EmptyState';

const roleVariant: Record<Role, 'info' | 'warning' | 'success' | 'danger'> = {
    OPERATOR: 'info',
    REVIEWER: 'warning',
    ANALYST: 'info',
    MANAGER: 'success',
    ADMIN: 'danger',
};

const roleOptions = [
    { label: 'All Roles', value: '' },
    { label: 'Operator', value: 'OPERATOR' },
    { label: 'Reviewer', value: 'REVIEWER' },
    { label: 'Manager', value: 'MANAGER' },
    { label: 'Admin', value: 'ADMIN' },
];

const statusOptions = [
    { label: 'All Status', value: '' },
    { label: 'Active', value: 'true' },
    { label: 'Disabled', value: 'false' },
];

const columns = [
    { key: 'username', label: 'Username' },
    { key: 'full_name', label: 'Full Name' },
    { key: 'role', label: 'Role' },
    { key: 'status', label: 'Status' },
    { key: 'created_at', label: 'Created' },
];

export function UserListPage() {
    const navigate = useNavigate();
    const userRole = useAuthStore((s) => s.user?.role);

    const [params, setParams] = useState<UserSearchParams>({
        page: 1,
        limit: 20,
    });

    const { data, isLoading, isError, refetch } = useUsers(params);

    const rows = (data?.data ?? []).map((u) => ({
        username: <span className="text-sm font-medium">{u.username}</span>,
        full_name: <span className="text-sm">{u.full_name}</span>,
        role: <Badge variant={roleVariant[u.role]}>{u.role}</Badge>,
        status: <Badge variant={u.is_active ? 'success' : 'muted'}>{u.is_active ? 'Active' : 'Disabled'}</Badge>,
        created_at: <span className="text-xs text-text-secondary">{new Date(u.created_at).toLocaleDateString()}</span>,
    }));

    const totalPages = data ? Math.ceil(data.total / data.limit) : 0;

    return (
        <ListPageTemplate
            header={
                <PageHeader
                    title="Users"
                    subtitle={data ? `${data.total} total users` : undefined}
                    actions={
                        userRole === 'ADMIN' ? (
                            <Button onClick={() => navigate({ to: '/users/create' })}>Create User</Button>
                        ) : undefined
                    }
                />
            }
            filterBar={
                <FilterBar>
                    <Select
                        options={roleOptions}
                        value={params.role ?? ''}
                        onChange={(e) =>
                            setParams((p) => ({
                                ...p,
                                role: (e.target.value || undefined) as Role | undefined,
                                page: 1,
                            }))
                        }
                        placeholder="All Roles"
                    />
                    <Select
                        options={statusOptions}
                        value={params.is_active === undefined ? '' : String(params.is_active)}
                        onChange={(e) =>
                            setParams((p) => ({
                                ...p,
                                is_active: e.target.value === '' ? undefined : e.target.value === 'true',
                                page: 1,
                            }))
                        }
                        placeholder="All Status"
                    />
                </FilterBar>
            }
            table={
                isLoading ? (
                    <LoadingSkeleton variant="table" rows={8} />
                ) : isError ? (
                    <ErrorState onRetry={refetch} />
                ) : rows.length === 0 ? (
                    <EmptyState title="No users found" description="Try adjusting your filters." />
                ) : (
                    <TableShell
                        columns={columns}
                        data={rows}
                        onRowClick={(_row, idx) => {
                            const user = data!.data[idx];
                            navigate({ to: '/users/$userId', params: { userId: user.user_id } });
                        }}
                    />
                )
            }
            pagination={
                totalPages > 1 ? (
                    <Pagination
                        currentPage={params.page}
                        totalPages={totalPages}
                        onPageChange={(page) => setParams((p) => ({ ...p, page }))}
                    />
                ) : undefined
            }
        />
    );
}
