import type { TextareaHTMLAttributes } from 'react';
import { cn } from '~/utils/cn';

interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
    label?: string;
    error?: string;
    hint?: string;
}

export function Textarea({ label, error, hint, className, id, ...rest }: TextareaProps) {
    const textareaId = id || label?.toLowerCase().replace(/\s+/g, '-');

    return (
        <div className="flex flex-col gap-2">
            {label && (
                <label htmlFor={textareaId} className="text-sm font-semibold text-text-primary">
                    {label}
                </label>
            )}
            <textarea
                id={textareaId}
                className={cn(
                    'w-full px-4 py-3',
                    'text-base min-h-35 resize-y',
                    'bg-primary',
                    'border border-border-default',
                    'rounded-lg',
                    'outline-none transition-all duration-150',
                    'focus:border-accent-indigo focus:ring-1 focus:ring-accent-indigo',
                    'placeholder:text-text-tertiary',
                    error && 'border-status-danger',
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
