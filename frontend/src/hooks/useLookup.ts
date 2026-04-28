import { useQuery } from '@tanstack/react-query';
import { lookupService } from '~/services/lookupService';

export const lookupKeys = {
    customers: (q: string) => ['lookup', 'customers', q] as const,
    merchants: (q: string) => ['lookup', 'merchants', q] as const,
    channels: ['lookup', 'channels'] as const,
};

export function useSearchCustomers(query: string) {
    return useQuery({
        queryKey: lookupKeys.customers(query),
        queryFn: () => lookupService.searchCustomers(query, 10),
        enabled: query.length >= 2,
    });
}

export function useSearchMerchants(query: string) {
    return useQuery({
        queryKey: lookupKeys.merchants(query),
        queryFn: () => lookupService.searchMerchants(query, 10),
        enabled: query.length >= 2,
    });
}

export function useChannels() {
    return useQuery({
        queryKey: lookupKeys.channels,
        queryFn: () => lookupService.getChannels(),
    });
}
