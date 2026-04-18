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
    success: 'bg-emerald-50 text-emerald-700',
    warning: 'bg-amber-50 text-amber-700',
    danger: 'bg-red-50 text-red-700',
    info: 'bg-blue-50 text-blue-700',
    muted: 'bg-surface-card text-text-secondary',
};

const dotStyles: Record<BadgeVariant, string> = {
    default: 'bg-primary',
    success: 'bg-emerald-500',
    warning: 'bg-amber-500',
    danger: 'bg-red-500',
    info: 'bg-blue-500',
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
