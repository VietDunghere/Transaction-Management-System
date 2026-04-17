import { apiClient } from './apiClient';
import type { DashboardSummary, FraudTrendResponse } from '~/types/api';

export const dashboardService = {
    getSummary() {
        return apiClient.get<unknown, DashboardSummary>('/dashboard/summary');
    },

    getFraudTrend(days = 30) {
        return apiClient.get<unknown, FraudTrendResponse>('/dashboard/fraud-trend', {
            params: { days },
        });
    },
};
