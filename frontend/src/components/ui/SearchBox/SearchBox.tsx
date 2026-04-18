import { Search } from 'lucide-react';
import { cn } from '~/utils/cn';

interface SearchBoxProps {
    value?: string;
    onChange?: (value: string) => void;
    placeholder?: string;
    className?: string;
}

export function SearchBox({ value, onChange, placeholder = 'Search...', className }: SearchBoxProps) {
    return (
        <div className={cn('relative', className)}>
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-tertiary" />
            <input
                type="text"
                value={value}
                onChange={(e) => onChange?.(e.target.value)}
                placeholder={placeholder}
                className={cn(
                    'w-full pl-10 pr-4 py-3',
                    'text-base',
                    'bg-primary',
                    'border border-border-default',
                    'rounded-lg',
                    'outline-none transition-all duration-150',
                    'focus:border-accent-indigo focus:ring-1 focus:ring-accent-indigo',
                    'placeholder:text-text-tertiary',
                )}
            />
        </div>
    );
}
