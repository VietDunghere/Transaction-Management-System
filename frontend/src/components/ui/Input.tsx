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
                <label
                    htmlFor={inputId}
                    className="text-base font-bold text-[#1a1a1a]"
                >
                    {label}
                </label>
            )}
            <input
                id={inputId}
                className={cn(
                    'w-full px-4 py-3',
                    'text-base',
                    'bg-white brutal-border',
                    'rounded-sm',
                    'outline-none transition-all duration-150',
                    'focus:ring-2 focus:ring-[#1a1a1a] focus:ring-offset-1',
                    'placeholder:text-[#a3a3a3]',
                    error && 'border-[#ef4444] focus:ring-[#ef4444]',
                    rest.disabled && 'opacity-50 cursor-not-allowed bg-[#f5f5f0]',
                    className,
                )}
                {...rest}
            />
            {hint && !error && (
                <p className="text-sm text-[#a3a3a3]">{hint}</p>
            )}
            {error && (
                <p className="text-sm text-[#ef4444] font-bold">
                    {error}
                </p>
            )}
        </div>
    );
}
