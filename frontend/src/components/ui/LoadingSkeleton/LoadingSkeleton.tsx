import { cn } from '~/utils/cn';

interface LoadingSkeletonProps {
    variant?: 'table' | 'card' | 'form' | 'chart';
    rows?: number;
    className?: string;
}

function SkeletonLine({ width = '100%', height = '1rem' }: { width?: string; height?: string }) {
    return <div className="animate-pulse rounded-md bg-border-default" style={{ width, height }} />;
}

export function LoadingSkeleton({ variant = 'table', rows = 5, className }: LoadingSkeletonProps) {
    const cardClass = 'bg-surface-card rounded-xl';

    if (variant === 'card') {
        return (
            <div className={cn('p-8 space-y-5', cardClass, className)}>
                <SkeletonLine width="40%" height="0.875rem" />
                <SkeletonLine width="60%" height="2rem" />
                <SkeletonLine width="30%" height="0.875rem" />
            </div>
        );
    }

    if (variant === 'chart') {
        return (
            <div className={cn('p-8', cardClass, className)}>
                <SkeletonLine width="30%" height="1rem" />
                <div className="mt-8 flex items-end gap-2 h-[200px]">
                    {Array.from({ length: 8 }).map((_, i) => (
                        <div
                            key={i}
                            className="flex-1 animate-pulse rounded-t-md bg-border-default"
                            style={{ height: `${30 + Math.random() * 70}%` }}
                        />
                    ))}
                </div>
            </div>
        );
    }

    if (variant === 'form') {
        return (
            <div className={cn('p-8 space-y-8', cardClass, className)}>
                {Array.from({ length: rows }).map((_, i) => (
                    <div key={i} className="space-y-2">
                        <SkeletonLine width="20%" height="0.875rem" />
                        <SkeletonLine width="100%" height="2.75rem" />
                    </div>
                ))}
            </div>
        );
    }

    return (
        <div className={cn('overflow-hidden', cardClass, className)}>
            <div className="flex gap-6 px-6 py-4">
                {Array.from({ length: 4 }).map((_, i) => (
                    <SkeletonLine key={i} width={`${20 + i * 5}%`} height="0.875rem" />
                ))}
            </div>
            {Array.from({ length: rows }).map((_, i) => (
                <div key={i} className="flex gap-6 border-t border-[var(--color-border-default)] px-6 py-4">
                    {Array.from({ length: 4 }).map((_, j) => (
                        <SkeletonLine key={j} width={`${30 + j * 10}%`} height="1rem" />
                    ))}
                </div>
            ))}
        </div>
    );
}
