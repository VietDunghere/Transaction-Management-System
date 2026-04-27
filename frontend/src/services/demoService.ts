import { apiClient } from './apiClient';

export interface DemoStartConfig {
    rate: number;
    count: number | null;
    loan_pct: number;
}

export interface DemoEvent {
    seq: number;
    type: string;
    result: string;
    score: number | null;
    amount: number;
    info: string;
    timestamp: string;
}

export interface DemoStatus {
    running: boolean;
    started_by: string | null;
    started_at: string | null;
    config: DemoStartConfig | null;
    sent: number;
    stats: Record<string, number>;
    recent_events: DemoEvent[];
}

export const demoService = {
    start(config: DemoStartConfig) {
        return apiClient.post<unknown, DemoStatus>('/demo/start', config);
    },

    stop() {
        return apiClient.post<unknown, DemoStatus>('/demo/stop');
    },

    getStatus() {
        return apiClient.get<unknown, DemoStatus>('/demo/status');
    },
};
