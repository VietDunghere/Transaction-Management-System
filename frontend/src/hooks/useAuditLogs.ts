import { useQuery } from '@tanstack/react-query';
import { auditService } from '~/services/auditService';
import type { AuditLogSearchParams } from '~/types/searchParams';
import type { AuditEntityType } from '~/types/api';

export const auditKeys = {
    all: ['audit-logs'] as const,
    list: (params: AuditLogSearchParams) => ['audit-logs', 'list', params] as const,
    detail: (logId: string) => ['audit-logs', 'detail', logId] as const,
    entityTrail: (entityType: AuditEntityType, entityId: string) =>
        ['audit-logs', 'entity', entityType, entityId] as const,
};

export function useAuditLogs(params: AuditLogSearchParams) {
    return useQuery({
        queryKey: auditKeys.list(params),
        queryFn: () => auditService.getAuditLogs(params),
    });
}

export function useAuditLog(logId: string) {
    return useQuery({
        queryKey: auditKeys.detail(logId),
        queryFn: () => auditService.getAuditLog(logId),
        enabled: !!logId,
    });
}

export function useEntityAuditTrail(entityType: AuditEntityType, entityId: string) {
    return useQuery({
        queryKey: auditKeys.entityTrail(entityType, entityId),
        queryFn: () => auditService.getEntityAuditTrail(entityType, entityId),
        enabled: !!entityType && !!entityId,
    });
}
