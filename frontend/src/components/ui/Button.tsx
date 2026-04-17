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
    primary: 'bg-[#1a1a1a] text-white hover:bg-[#333]',
    secondary: 'bg-white text-[#1a1a1a] hover:bg-[#f5f5f0]',
    danger: 'bg-[#ef4444] text-white hover:bg-red-600',
    ghost: 'bg-transparent text-[#525252] hover:bg-[#f5f5f0]',
};

const sizeClass: Record<ButtonSize, string> = {
    sm: 'px-4 py-2 text-sm gap-2',
    md: 'px-5 py-2.5 text-base gap-2',
    lg: 'px-8 py-3.5 text-lg gap-3',
};

export function Button({
    variant = 'primary',
    size = 'md',
    icon,
    loading = false,
    disabled,
    className,
    children,
    style,
    ...rest
}: ButtonProps) {
    const isDisabled = disabled || loading;
    const isGhost = variant === 'ghost';

    return (
        <button
            className={cn(
                'inline-flex items-center justify-center font-bold rounded cursor-pointer select-none',
                'transition-all duration-150',
                'hover:-translate-x-0.5 hover:-translate-y-0.5',
                'active:translate-x-0.5 active:translate-y-0.5',
                variantClass[variant],
                sizeClass[size],
                isDisabled && 'pointer-events-none opacity-50',
                className,
            )}
            style={{
                border: isGhost ? 'none' : '2px solid #1a1a1a',
                boxShadow: isGhost ? 'none' : '3px 3px 0 0 #1a1a1a',
                ...style,
            }}
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
