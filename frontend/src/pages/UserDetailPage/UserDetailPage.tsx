import { useState } from 'react';
import { useParams, useNavigate } from '@tanstack/react-router';
import { useUser, useDisableUser, useEnableUser, useUpdateUserRole } from '~/hooks/useUsers';
import { useAuthStore } from '~/stores/useAuthStore';
import type { Role } from '~/types/api';
import { PageHeader } from '~/components/templates/PageHeader/PageHeader';
import { DetailPageTemplate } from '~/components/templates/DetailPageTemplate/DetailPageTemplate';
import { Card } from '~/components/ui/Card/Card';
import { KeyValueRow } from '~/components/ui/KeyValueRow/KeyValueRow';
import { Badge } from '~/components/ui/Badge/Badge';
import { SectionHeader } from '~/components/ui/SectionHeader/SectionHeader';
import { Button } from '~/components/ui/Button/Button';
import { Modal } from '~/components/ui/Modal/Modal';
import { Select } from '~/components/ui/Select/Select';
import { LoadingSkeleton } from '~/components/ui/LoadingSkeleton/LoadingSkeleton';
import { ErrorState } from '~/components/ui/ErrorState/ErrorState';

const roleVariant: Record<Role, 'info' | 'warning' | 'success' | 'danger'> = {
    OPERATOR: 'info',
    REVIEWER: 'warning',
    MANAGER: 'success',
    ADMIN: 'danger',
};

const roleOptions = [
    { label: 'Operator', value: 'OPERATOR' },
    { label: 'Reviewer', value: 'REVIEWER' },
    { label: 'Manager', value: 'MANAGER' },
];

export function UserDetailPage() {
    const { userId } = useParams({ strict: false }) as { userId: string };
    const navigate = useNavigate();
    const currentUser = useAuthStore((s) => s.user);
    const { data: userData, isLoading, isError, refetch } = useUser(userId);
    const disableUser = useDisableUser();
    const enableUser = useEnableUser();
    const updateRole = useUpdateUserRole();

    const [roleModal, setRoleModal] = useState(false);
    const [selectedRole, setSelectedRole] = useState<Exclude<Role, 'ADMIN'>>('OPERATOR');

    if (isLoading) return <LoadingSkeleton variant="card" />;
    if (isError || !userData) return <ErrorState onRetry={refetch} />;

    const isAdmin = currentUser?.role === 'ADMIN';
    const isSelf = currentUser?.user_id === userData.user_id;

    const handleToggleStatus = () => {
        if (userData.is_active) {
            disableUser.mutate(userId);
        } else {
            enableUser.mutate(userId);
        }
    };

    const handleRoleChange = () => {
        updateRole.mutate(
            { userId, role: selectedRole },
            {
                onSuccess: () => setRoleModal(false),
            },
        );
    };

    return (
        <>
            <DetailPageTemplate
                header={
                    <PageHeader
                        title={userData.full_name}
                        subtitle={`@${userData.username}`}
                        actions={
                            <div className="flex items-center gap-2">
                                {isAdmin && !isSelf && (
                                    <>
                                        <Button
                                            variant={userData.is_active ? 'danger' : 'primary'}
                                            onClick={handleToggleStatus}
                                            loading={disableUser.isPending || enableUser.isPending}
                                        >
                                            {userData.is_active ? 'Disable' : 'Enable'}
                                        </Button>
                                        <Button
                                            onClick={() => {
                                                setSelectedRole(
                                                    userData.role === 'ADMIN'
                                                        ? 'OPERATOR'
                                                        : (userData.role as Exclude<Role, 'ADMIN'>),
                                                );
                                                setRoleModal(true);
                                            }}
                                        >
                                            Change Role
                                        </Button>
                                    </>
                                )}
                                <Button variant="ghost" onClick={() => navigate({ to: '/users' })}>
                                    Back to List
                                </Button>
                            </div>
                        }
                    />
                }
                summary={
                    <div className="flex flex-col gap-5">
                        <div className="flex flex-col items-start gap-1">
                            <span className="text-xs font-medium text-text-secondary">Role</span>
                            <Badge variant={roleVariant[userData.role]}>{userData.role}</Badge>
                        </div>
                        <div className="flex flex-col items-start gap-1">
                            <span className="text-xs font-medium text-text-secondary">Status</span>
                            <Badge variant={userData.is_active ? 'success' : 'muted'} dot>
                                {userData.is_active ? 'Active' : 'Disabled'}
                            </Badge>
                        </div>
                        <div className="flex flex-col gap-1">
                            <span className="text-xs font-medium text-text-secondary">Email</span>
                            <span className="text-sm break-all">{userData.email}</span>
                        </div>
                        <div className="flex flex-col gap-1">
                            <span className="text-xs font-medium text-text-secondary">Joined</span>
                            <span className="text-sm">{new Date(userData.created_at).toLocaleDateString()}</span>
                        </div>
                    </div>
                }
                info={
                    <Card>
                        <SectionHeader title="User Details" />
                        <div className="flex flex-col gap-1 mt-4">
                            <KeyValueRow
                                label="User ID"
                                value={<span className="font-mono text-xs">{userData.user_id}</span>}
                            />
                            <KeyValueRow label="Username" value={userData.username} />
                            <KeyValueRow label="Full Name" value={userData.full_name} />
                            <KeyValueRow label="Email" value={userData.email} />
                            <KeyValueRow
                                label="Role"
                                value={<Badge variant={roleVariant[userData.role]}>{userData.role}</Badge>}
                            />
                            <KeyValueRow
                                label="Status"
                                value={
                                    <Badge variant={userData.is_active ? 'success' : 'muted'}>
                                        {userData.is_active ? 'Active' : 'Disabled'}
                                    </Badge>
                                }
                            />
                            <KeyValueRow label="Created At" value={new Date(userData.created_at).toLocaleString()} />
                        </div>
                    </Card>
                }
            />

            {/* Role Change Modal */}
            <Modal
                isOpen={roleModal}
                onClose={() => setRoleModal(false)}
                title="Change User Role"
                footer={
                    <div className="flex justify-end gap-2">
                        <Button variant="ghost" onClick={() => setRoleModal(false)}>
                            Cancel
                        </Button>
                        <Button onClick={handleRoleChange} loading={updateRole.isPending}>
                            Update Role
                        </Button>
                    </div>
                }
            >
                <Select
                    label="New Role"
                    options={roleOptions}
                    value={selectedRole}
                    onChange={(e) => setSelectedRole(e.target.value as Exclude<Role, 'ADMIN'>)}
                />
                {updateRole.isError && (
                    <p className="text-xs text-status-danger mt-2">Failed to update role. Please try again.</p>
                )}
            </Modal>
        </>
    );
}
