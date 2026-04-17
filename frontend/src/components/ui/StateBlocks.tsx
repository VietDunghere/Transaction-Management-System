import type { ReactNode } from 'react';
import { RefreshCw, Inbox, AlertTriangle, WifiOff, ShieldX } from 'lucide-react';
import { cn } from '~/utils/cn';
import { Button } from './Button';

/* ============================================================
   LoadingSkeleton — Animated placeholder blocks
   ============================================================ */

interface LoadingSkeletonProps {
    variant?: 'table' | 'card' | 'form' | 'chart';
    rows?: number;
    className?: string;
}

function SkeletonLine({ width = '100%', height = '16px' }: { width?: string; height?: string }) {
    return (
        <div
            className="animate-pulse rounded-sm bg-[#d4d4d4]"
            style={{ width, height }}
        />
    );
}

const brutalCard: React.CSSProperties = {
    background: '#ffffff',
    border: '2px solid #1a1a1a',
    boxShadow: '4px 4px 0 0 #1a1a1a',
    borderRadius: '6px',
};

export function LoadingSkeleton({ variant = 'table', rows = 5, className }: LoadingSkeletonProps) {
    if (variant === 'card') {
        return (
            <div className={cn('p-8 space-y-5', className)} style={brutalCard}>
                <SkeletonLine width="40%" height="14px" />
                <SkeletonLine width="60%" height="36px" />
                <SkeletonLine width="30%" height="14px" />
            </div>
        );
    }

    if (variant === 'chart') {
        return (
            <div className={cn('p-8', className)} style={brutalCard}>
                <SkeletonLine width="30%" height="18px" />
                <div className="mt-8 flex items-end gap-3 h-[220px]">
                    {Array.from({ length: 8 }).map((_, i) => (
                        <div
                            key={i}
                            className="flex-1 animate-pulse rounded-t-sm bg-[#d4d4d4]"
                            style={{ height: `${30 + Math.random() * 70}%` }}
                        />
                    ))}
                </div>
                <div className="mt-2 flex justify-between">
                    {Array.from({ length: 8 }).map((_, i) => (
                        <SkeletonLine key={i} width="32px" height="10px" />
                    ))}
                </div>
            </div>
        );
    }

    if (variant === 'form') {
        return (
            <div className={cn('p-8 space-y-8', className)} style={brutalCard}>
                {Array.from({ length: rows }).map((_, i) => (
                    <div key={i} className="space-y-2">
                        <SkeletonLine width="20%" height="14px" />
                        <SkeletonLine width="100%" height="42px" />
                    </div>
                ))}
            </div>
        );
    }

    // Table variant (default)
    return (
        <div className={cn('overflow-hidden', className)} style={brutalCard}>
            {/* Header row */}
            <div className="flex gap-6 bg-[#f5f5f0] px-6 py-4">
                {Array.from({ length: 4 }).map((_, i) => (
                    <SkeletonLine key={i} width={`${20 + i * 5}%`} height="14px" />
                ))}
            </div>
            {/* Data rows */}
            {Array.from({ length: rows }).map((_, i) => (
                <div
                    key={i}
                    className="flex gap-6 border-b border-[#d4d4d4] px-6 py-4"
                >
                    {Array.from({ length: 4 }).map((_, j) => (
                        <SkeletonLine key={j} width={`${30 + j * 10}%`} height="16px" />
                    ))}
                </div>
            ))}
        </div>
    );
}

/* ============================================================
   EmptyState — No data placeholder
   ============================================================ */

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
        <div
            className={cn(
                'flex flex-col items-center justify-center py-16 px-6',
                'text-center',
                className,
            )}
        >
            <div className="mb-6 flex size-20 items-center justify-center rounded-full bg-[#f5f5f0] text-[#a3a3a3]">
                {icon || <Inbox size={36} />}
            </div>
            <h3 className="text-2xl font-black mb-2">
                {title}
            </h3>
            <p className="text-base text-[#525252] max-w-sm">
                {description}
            </p>
            {action && <div className="mt-6">{action}</div>}
        </div>
    );
}

/* ============================================================
   ErrorState — Error display block
   ============================================================ */

type ErrorType = 'network' | 'unauthorized' | 'unknown';

interface ErrorStateProps {
    type?: ErrorType;
    title?: string;
    description?: string;
    onRetry?: () => void;
    className?: string;
}

const errorConfig: Record<ErrorType, { icon: ReactNode; title: string; description: string }> = {
    network: {
        icon: <WifiOff size={28} />,
        title: 'Connection Error',
        description: 'Unable to reach the server. Please check your network connection and try again.',
    },
    unauthorized: {
        icon: <ShieldX size={28} />,
        title: 'Access Denied',
        description: 'You do not have permission to view this resource. Please contact your administrator.',
    },
    unknown: {
        icon: <AlertTriangle size={28} />,
        title: 'Something went wrong',
        description: 'An unexpected error occurred. Please try again later.',
    },
};

export function ErrorState({ type = 'unknown', title, description, onRetry, className }: ErrorStateProps) {
    const config = errorConfig[type];

    return (
        <div
            className={cn(
                'p-8',
                'flex flex-col items-center justify-center text-center',
                className,
            )}
            style={{ ...brutalCard, borderColor: '#ef4444' }}
        >
            <div className="mb-6 flex size-20 items-center justify-center rounded-full bg-red-50 text-[#ef4444]">
                {config.icon}
            </div>
            <h3 className="text-2xl font-black mb-2">
                {title || config.title}
            </h3>
            <p className="text-base text-[#525252] max-w-sm">
                {description || config.description}
            </p>
            {onRetry && (
                <div className="mt-6">
                    <Button variant="secondary" size="sm" icon={<RefreshCw size={14} />} onClick={onRetry}>
                        Retry
                    </Button>
                </div>
            )}
        </div>
    );
}
