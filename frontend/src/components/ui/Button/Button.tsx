import type { ButtonHTMLAttributes, ReactNode } from 'react';
import { cn } from '~/utils/cn';

type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'ghost';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: ButtonVariant;
    size?: ButtonSize;
    icon?: ReactNode;
    loading?: boolean;
}

const variantClass: Record<ButtonVariant, string> = {
    primary: 'bg-text-primary text-bg-primary hover:opacity-90',
    secondary:
        'bg-surface-card text-text-primary border border-border-default hover:bg-subtle',
    danger: 'bg-status-danger text-white hover:opacity-90',
    ghost: 'bg-transparent text-text-secondary hover:bg-subtle hover:text-text-primary',
};

const sizeClass: Record<ButtonSize, string> = {
    sm: 'px-4 py-1.5 text-sm gap-2',
    md: 'px-5 py-2.5 text-base gap-2',
    lg: 'px-8 py-3.5 text-base gap-3',
};

export function Button({
    variant = 'primary',
    size = 'md',
    icon,
    loading = false,
    disabled,
    className,
    children,
    ...rest
}: ButtonProps) {
    const isDisabled = disabled || loading;

    return (
        <button
            className={cn(
                'inline-flex items-center justify-center font-semibold rounded-lg cursor-pointer select-none',
                'transition-all duration-150',
                variantClass[variant],
                sizeClass[size],
                isDisabled && 'pointer-events-none opacity-50',
                className,
            )}
            disabled={isDisabled}
            {...rest}
        >
            {loading ? (
                <span className="size-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
            ) : (
                icon && <span className="shrink-0">{icon}</span>
            )}
            {children}
        </button>
    );
}
