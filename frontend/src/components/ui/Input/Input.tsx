import type { InputHTMLAttributes } from 'react';
import { cn } from '~/utils/cn';

type InputSize = 'sm' | 'md' | 'lg';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
    label?: string;
    error?: string;
    hint?: string;
    inputSize?: InputSize;
}

const sizeStyles: Record<InputSize, string> = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2.5 text-sm',
    lg: 'px-4 py-3 text-base',
};

export function Input({ label, error, hint, inputSize = 'md', className, id, ...rest }: InputProps) {
    const inputId = id || label?.toLowerCase().replace(/\s+/g, '-');

    return (
        <div className="flex flex-col gap-1.5">
            {label && (
                <label htmlFor={inputId} className="text-sm font-semibold text-text-primary">
                    {label}
                </label>
            )}
            <input
                id={inputId}
                className={cn(
                    'w-full',
                    sizeStyles[inputSize],
                    'bg-primary',
                    'border border-border-default',
                    'rounded-lg',
                    'outline-none transition-all duration-150',
                    'focus:border-accent-indigo focus:ring-1 focus:ring-accent-indigo',
                    'placeholder:text-text-tertiary',
                    error && 'border-status-danger focus:ring-status-danger',
                    rest.disabled && 'opacity-50 cursor-not-allowed bg-surface-card',
                    className,
                )}
                {...rest}
            />
            {hint && !error && <p className="text-sm text-text-secondary">{hint}</p>}
            {error && <p className="text-sm text-status-danger font-semibold">{error}</p>}
        </div>
    );
}
