import type { InputHTMLAttributes } from 'react';
import { cn } from '~/utils/cn';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
    label?: string;
    error?: string;
    hint?: string;
}

export function Input({ label, error, hint, className, id, ...rest }: InputProps) {
    const inputId = id || label?.toLowerCase().replace(/\s+/g, '-');

    return (
        <div className="flex flex-col gap-2">
            {label && (
                <label htmlFor={inputId} className="text-sm font-semibold text-text-primary">
                    {label}
                </label>
            )}
            <input
                id={inputId}
                className={cn(
                    'w-full px-4 py-3',
                    'text-base',
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
