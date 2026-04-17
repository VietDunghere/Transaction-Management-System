import type { SelectHTMLAttributes } from 'react';
import { ChevronDown } from 'lucide-react';
import { cn } from '~/utils/cn';

interface SelectOption {
    label: string;
    value: string;
}

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
    label?: string;
    error?: string;
    options: SelectOption[];
    placeholder?: string;
}

export function Select({ label, error, options, placeholder, className, id, ...rest }: SelectProps) {
    const selectId = id || label?.toLowerCase().replace(/\s+/g, '-');

    return (
        <div className="flex flex-col gap-2">
            {label && (
                <label
                    htmlFor={selectId}
                    className="text-base font-bold text-[#1a1a1a]"
                >
                    {label}
                </label>
            )}
            <div className="relative">
                <select
                    id={selectId}
                    className={cn(
                        'w-full appearance-none',
                        'px-4 py-3 pr-9',
                        'text-base',
                        'bg-white brutal-border',
                        'rounded-sm',
                        'outline-none transition-all duration-150',
                        'focus:ring-2 focus:ring-[#1a1a1a] focus:ring-offset-1',
                        'cursor-pointer',
                        error && 'border-[#ef4444]',
                        rest.disabled && 'opacity-50 cursor-not-allowed bg-[#f5f5f0]',
                        className,
                    )}
                    {...rest}
                >
                    {placeholder && (
                        <option value="" disabled>
                            {placeholder}
                        </option>
                    )}
                    {options.map((opt) => (
                        <option key={opt.value} value={opt.value}>
                            {opt.label}
                        </option>
                    ))}
                </select>
                <ChevronDown
                    size={16}
                    className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-[#a3a3a3]"
                />
            </div>
            {error && (
                <p className="text-sm text-[#ef4444] font-bold">
                    {error}
                </p>
            )}
        </div>
    );
}
