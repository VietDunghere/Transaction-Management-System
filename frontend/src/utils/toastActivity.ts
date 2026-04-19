import { toast } from 'sonner';
import { useActivityStore } from '~/stores/useActivityStore';
import type { ActivityType } from '~/stores/useActivityStore';

export function trackActivity(type: ActivityType, detail: string): void {
    useActivityStore.getState().addActivity(type, detail);
}

export function toastSuccessWithActivity(message: string): void {
    toast.success(message);
    useActivityStore.getState().addFromSuccessToast(message);
}
