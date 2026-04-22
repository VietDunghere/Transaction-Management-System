import { useQuery } from '@tanstack/react-query';
import { dataLakeService } from '~/services/dataLakeService';
import type { DataLakeSearchParams } from '~/types/searchParams';

export const dataLakeKeys = {
    all: ['datalake'] as const,
    list: (params: DataLakeSearchParams) => ['datalake', 'list', params] as const,
};

export function useDataLakeSnapshots(params: DataLakeSearchParams) {
    return useQuery({
        queryKey: dataLakeKeys.list(params),
        queryFn: () => dataLakeService.getSnapshots(params),
    });
}
