import { apiClient } from './apiClient';
import type { AuditLog, AuditEntityType, PagedResponse } from '~/types/api';
import type { AuditLogSearchParams } from '~/types/searchParams';

export const auditService = {
    getAuditLogs(params: AuditLogSearchParams) {
        return apiClient.get<unknown, PagedResponse<AuditLog>>('/audit-logs', { params });
    },

    getAuditLog(logId: string) {
        return apiClient.get<unknown, AuditLog>(`/audit-logs/${logId}`);
    },

    getEntityAuditTrail(entityType: AuditEntityType, entityId: string) {
        return apiClient.get<unknown, AuditLog[]>(`/audit-logs/entities/${entityType}/${entityId}`);
    },
};
