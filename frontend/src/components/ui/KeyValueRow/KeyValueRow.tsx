import type { ReactNode } from 'react';
import { cn } from '~/utils/cn';

interface KeyValueRowProps {
    label: string;
    value: ReactNode;
    className?: string;
}

export function KeyValueRow({ label, value, className }: KeyValueRowProps) {
    return (
        <div
            className={cn(
                'flex items-start justify-between py-4 border-b border-[var(--color-border-default)] last:border-b-0',
                className,
            )}
        >
            <span className="text-base text-[var(--color-text-secondary)] shrink-0 mr-6">{label}</span>
            <span className="text-base text-right text-[var(--color-text-primary)]">{value}</span>
        </div>
    );
}
