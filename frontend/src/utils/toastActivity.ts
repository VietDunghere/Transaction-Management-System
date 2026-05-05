import { toast } from 'sonner';
import { useActivityStore } from '~/stores/useActivityStore';
import type { ActivityType } from '~/stores/useActivityStore';

export function trackActivity(type: ActivityType, detail: string): void {
    try {
        useActivityStore.getState().addActivity(type, detail);
    } catch {
        // Ignore non-critical activity-log errors to avoid interrupting successful flows.
    }
}

export function toastSuccessWithActivity(message: string): void {
    toast.success(message);
    try {
        useActivityStore.getState().addFromSuccessToast(message);
    } catch {
        // Ignore non-critical activity-log errors to avoid interrupting successful flows.
    }
}
