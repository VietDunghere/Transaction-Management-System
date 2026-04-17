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
                <label
                    htmlFor={textareaId}
                    className="text-base font-bold text-[#1a1a1a]"
                >
                    {label}
                </label>
            )}
            <textarea
                id={textareaId}
                className={cn(
                    'w-full px-4 py-3',
                    'text-base min-h-[140px] resize-y',
                    'bg-white brutal-border',
                    'rounded-sm',
                    'outline-none transition-all duration-150',
                    'focus:ring-2 focus:ring-[#1a1a1a] focus:ring-offset-1',
                    'placeholder:text-[#a3a3a3]',
                    error && 'border-[#ef4444]',
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
