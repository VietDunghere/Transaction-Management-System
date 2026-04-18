import type { ReactNode } from 'react';
import { Inbox } from 'lucide-react';
import { cn } from '~/utils/cn';

interface EmptyStateProps {
    icon?: ReactNode;
    title?: string;
    description?: string;
    action?: ReactNode;
    className?: string;
}

export function EmptyState({
    icon,
    title = 'No data found',
    description = 'There are no items to display at the moment.',
    action,
    className,
}: EmptyStateProps) {
    return (
        <div className={cn('flex flex-col items-center justify-center py-16 px-8', 'text-center', className)}>
            <div className="mb-5 flex size-16 items-center justify-center rounded-full bg-surface-card text-text-secondary">
                {icon || <Inbox size={28} />}
            </div>
            <h3 className="text-base font-semibold mb-2 text-text-primary">{title}</h3>
            <p className="text-sm text-text-secondary max-w-sm leading-relaxed">{description}</p>
            {action && <div className="mt-6">{action}</div>}
        </div>
    );
}
