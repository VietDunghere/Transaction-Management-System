import { apiClient } from './apiClient';
import type { EtlJob, TriggerEtlRequest, PagedResponse } from '~/types/api';
import type { EtlLogSearchParams } from '~/types/searchParams';

export const etlService = {
    getEtlLogs(params: EtlLogSearchParams) {
        return apiClient.get<unknown, PagedResponse<EtlJob>>('/etl/logs', { params });
    },

    triggerEtl(data: TriggerEtlRequest) {
        return apiClient.post<unknown, EtlJob>('/etl/run', data);
    },
};
