import { apiClient } from './apiClient';

export interface CustomerSearchItem {
    customer_id: string;
    full_name: string;
    customer_code: string;
}

export interface MerchantSearchItem {
    merchant_id: string;
    merchant_name: string;
    merchant_code: string;
    merchant_category: string | null;
}

export interface ChannelItem {
    channel_id: number;
    channel_name: string;
}

export const lookupService = {
    searchCustomers(q: string, limit = 10) {
        return apiClient.get<unknown, CustomerSearchItem[]>('/lookup/customers', {
            params: { q, limit },
        });
    },

    searchMerchants(q: string, limit = 10) {
        return apiClient.get<unknown, MerchantSearchItem[]>('/lookup/merchants', {
            params: { q, limit },
        });
    },

    getChannels() {
        return apiClient.get<unknown, ChannelItem[]>('/lookup/channels');
    },
};
