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
    default: 'bg-[#1a1a1a] text-white border-[#1a1a1a]',
    success: 'bg-emerald-100 text-emerald-800 border-emerald-300',
    warning: 'bg-amber-100 text-amber-800 border-amber-300',
    danger: 'bg-red-100 text-red-800 border-red-300',
    info: 'bg-blue-100 text-blue-800 border-blue-300',
    muted: 'bg-[#f5f5f0] text-[#525252] border-[#d4d4d4]',
};

const dotStyles: Record<BadgeVariant, string> = {
    default: 'bg-[#1a1a1a]',
    success: 'bg-emerald-500',
    warning: 'bg-amber-500',
    danger: 'bg-red-500',
    info: 'bg-blue-500',
    muted: 'bg-[#a3a3a3]',
};

export function Badge({ variant = 'default', children, className, dot = false }: BadgeProps) {
    return (
        <span
            className={cn(
                'inline-flex items-center gap-1.5',
                'px-3 py-1',
                'text-sm font-semibold',
                'rounded border',
                variantStyles[variant],
                className,
            )}
        >
            {dot && <span className={cn('size-1.5 rounded-full', dotStyles[variant])} />}
            {children}
        </span>
    );
}
