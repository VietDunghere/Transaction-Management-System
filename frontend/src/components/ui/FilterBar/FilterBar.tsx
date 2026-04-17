import type { ReactNode } from 'react';
import { cn } from '~/utils/cn';

interface FilterBarProps {
    children: ReactNode;
    className?: string;
}

export function FilterBar({ children, className }: FilterBarProps) {
    return <div className={cn('flex flex-wrap items-end gap-4', className)}>{children}</div>;
}
