import type { ReactNode } from 'react';
import { cn } from '~/utils/cn';

interface SectionHeaderProps {
    title: string;
    action?: ReactNode;
    className?: string;
}

export function SectionHeader({ title, action, className }: SectionHeaderProps) {
    return (
        <div className={cn('flex items-center justify-between', className)}>
            <h2 className="text-lg font-semibold text-text-primary">{title}</h2>
            {action}
        </div>
    );
}
