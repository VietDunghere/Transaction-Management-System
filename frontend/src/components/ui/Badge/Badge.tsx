import type { ReactNode } from 'react';
import { cn } from '~/utils/cn';

type BadgeVariant = 'default' | 'success' | 'warning' | 'danger' | 'info' | 'muted';

interface BadgeProps {
    variant?: BadgeVariant;
    children: ReactNode;
    className?: string;
    dot?: boolean;
}

const variantStyles: Record<BadgeVariant, string> = {
    default: 'bg-text-primary text-bg-primary',
    success: 'bg-badge-success-bg text-badge-success-text',
    warning: 'bg-badge-warning-bg text-badge-warning-text',
    danger: 'bg-badge-danger-bg text-badge-danger-text',
    info: 'bg-badge-info-bg text-badge-info-text',
    muted: 'bg-surface-card text-text-secondary',
};

const dotStyles: Record<BadgeVariant, string> = {
    default: 'bg-primary',
    success: 'bg-badge-success-dot',
    warning: 'bg-badge-warning-dot',
    danger: 'bg-badge-danger-dot',
    info: 'bg-badge-info-dot',
    muted: 'bg-text-secondary',
};

export function Badge({ variant = 'default', children, className, dot = false }: BadgeProps) {
    return (
        <span
            className={cn(
                'inline-flex items-center gap-1.5',
                'px-3 py-1',
                'text-sm font-semibold',
                'rounded-md',
                variantStyles[variant],
                className,
            )}
        >
            {dot && <span className={cn('size-1.5 rounded-full', dotStyles[variant])} />}
            {children}
        </span>
    );
}
