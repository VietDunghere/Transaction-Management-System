import type { ReactNode } from 'react';
import { cn } from '~/utils/cn';

interface TimelineItemProps {
    title: string;
    description?: string;
    timestamp: string;
    icon?: ReactNode;
    variant?: 'default' | 'success' | 'warning' | 'danger';
}

const timelineDotStyles = {
    default: 'bg-[var(--color-text-primary)]',
    success: 'bg-[var(--color-status-success)]',
    warning: 'bg-[var(--color-status-warning)]',
    danger: 'bg-[var(--color-status-danger)]',
};

export function TimelineItem({ title, description, timestamp, icon, variant = 'default' }: TimelineItemProps) {
    return (
        <div className="relative flex gap-4 pb-8 last:pb-0">
            <div className="flex flex-col items-center">
                <div
                    className={cn(
                        'flex size-8 shrink-0 items-center justify-center rounded-full',
                        timelineDotStyles[variant],
                        'text-white',
                    )}
                >
                    {icon || <span className="size-2 rounded-full bg-current" />}
                </div>
                <div className="w-px flex-1 bg-[var(--color-border-default)]" />
            </div>
            <div className="flex-1 pt-1">
                <p className="text-base font-semibold text-[var(--color-text-primary)]">{title}</p>
                {description && <p className="mt-1 text-base text-[var(--color-text-secondary)]">{description}</p>}
                <p className="mt-1 text-sm text-[var(--color-text-secondary)]">{timestamp}</p>
            </div>
        </div>
    );
}
