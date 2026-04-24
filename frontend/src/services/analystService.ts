import { apiClient } from './apiClient';
import type {
    ThresholdListResponse,
    ThresholdUpdateRequest,
    FraudModelPerformance,
    LoanModelPerformance,
} from '~/types/api';

export const analystService = {
    getThresholds() {
        return apiClient.get<unknown, ThresholdListResponse>('/analyst/thresholds');
    },

    updateThresholds(data: ThresholdUpdateRequest) {
        return apiClient.patch<unknown, ThresholdListResponse>('/analyst/thresholds', data);
    },

    getFraudPerformance(days = 30) {
        return apiClient.get<unknown, FraudModelPerformance>('/analyst/model-performance/fraud', { params: { days } });
    },

    getLoanPerformance(days = 30) {
        return apiClient.get<unknown, LoanModelPerformance>('/analyst/model-performance/loan', { params: { days } });
    },
};
