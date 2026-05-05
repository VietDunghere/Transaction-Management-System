import { create } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';
import { useAuthStore } from '~/stores/useAuthStore';

export type ActivityType = 'add' | 'modify' | 'delete' | 'success';

export interface ActivityItem {
    id: string;
    avatar: string;
    name: string;
    action: string;
    timestamp: string;
}

interface ActivityState {
    activities: ActivityItem[];
    addActivity: (type: ActivityType, detail: string) => void;
    addFromSuccessToast: (message: string) => void;
    clearActivities: () => void;
}

const STORAGE_KEY = 'activity_log';
const MAX_ACTIVITIES = 50;


function toInitials(value: string): string {
    const parts = value.trim().split(/\s+/).filter(Boolean);

    if (parts.length === 0) {
        return 'YY';
    }

    return parts
        .slice(0, 2)
        .map((part) => part[0]?.toUpperCase() ?? '')
        .join('');
}

function actorInfo(): { name: string; avatar: string } {
    const user = useAuthStore.getState().user;
    const name = user?.full_name?.trim() || user?.username || 'You';

    return {
        name,
        avatar: toInitials(name),
    };
}

function mapTypeToAction(type: ActivityType, detail: string): string {
    const cleanDetail = detail.trim().replace(/[.]$/, '');

    if (type === 'add') {
        return `added data (${cleanDetail})`;
    }

    if (type === 'modify') {
        return `modified data (${cleanDetail})`;
    }

    if (type === 'delete') {
        return `deleted data (${cleanDetail})`;
    }

    return `completed action (${cleanDetail})`;
}

function inferTypeFromSuccessMessage(message: string): ActivityType {
    const normalized = message.toLowerCase();

    if (/delete|deleted|remove|removed/.test(normalized)) {
        return 'delete';
    }

    if (/create|created|submit|submitted|add|added|triggered/.test(normalized)) {
        return 'add';
    }

    if (/update|updated|change|changed|enable|enabled|disable|disabled|assign|assigned|decision/.test(normalized)) {
        return 'modify';
    }

    return 'success';
}

function appendActivity(list: ActivityItem[], nextItem: ActivityItem): ActivityItem[] {
    const next = [nextItem, ...list];
    return next.slice(0, MAX_ACTIVITIES);
}

export function formatActivityTime(timestamp: string): string {
    const then = new Date(timestamp).getTime();
    const now = Date.now();
    const diffMs = Math.max(0, now - then);
    const minute = 60_000;
    const hour = 60 * minute;
    const day = 24 * hour;

    if (diffMs < minute) {
        return 'Just now';
    }

    if (diffMs < hour) {
        const minutes = Math.floor(diffMs / minute);
        return `${minutes} min ago`;
    }

    if (diffMs < day) {
        const hours = Math.floor(diffMs / hour);
        return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    }

    return new Intl.DateTimeFormat('en-US', {
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
    }).format(new Date(timestamp));
}

export const useActivityStore = create<ActivityState>()(
    persist(
        (set) => ({
            activities: [],
            addActivity: (type, detail) => {
                const actor = actorInfo();
                const timestamp = new Date().toISOString();

                const nextItem: ActivityItem = {
                    id: crypto.randomUUID(),
                    avatar: actor.avatar,
                    name: actor.name,
                    action: mapTypeToAction(type, detail),
                    timestamp,
                };

                set((state) => ({
                    activities: appendActivity(state.activities, nextItem),
                }));
            },
            addFromSuccessToast: (message) => {
                const type = inferTypeFromSuccessMessage(message);
                const actor = actorInfo();
                const timestamp = new Date().toISOString();

                const nextItem: ActivityItem = {
                    id: crypto.randomUUID(),
                    avatar: actor.avatar,
                    name: actor.name,
                    action: mapTypeToAction(type, message),
                    timestamp,
                };

                set((state) => ({
                    activities: appendActivity(state.activities, nextItem),
                }));
            },
            clearActivities: () => set({ activities: [] }),
        }),
        {
            name: STORAGE_KEY,
            storage: createJSONStorage(() => localStorage),
            partialize: (state) => ({ activities: state.activities }),
        },
    ),
);
