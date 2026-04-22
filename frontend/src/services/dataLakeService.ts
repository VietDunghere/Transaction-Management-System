import { apiClient } from './apiClient';
import type { DataLakeSnapshot, PagedResponse } from '~/types/api';
import type { DataLakeSearchParams } from '~/types/searchParams';

export const dataLakeService = {
    getSnapshots(params: DataLakeSearchParams) {
        return apiClient.get<unknown, PagedResponse<DataLakeSnapshot>>('/datalake/snapshots', { params });
    },
};
