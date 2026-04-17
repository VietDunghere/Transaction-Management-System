import type { ReactNode } from 'react';
import { RefreshCw, AlertTriangle, WifiOff, ShieldX } from 'lucide-react';
import { cn } from '~/utils/cn';
import { Button } from '~/components/ui/Button';

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
                'p-8 rounded-xl bg-surface-card',
                'flex flex-col items-center justify-center text-center',
                className,
            )}
        >
            <div className="mb-5 flex size-16 items-center justify-center rounded-full bg-red-50 text-[var(--color-status-danger)]">
                {config.icon}
            </div>
            <h3 className="text-base font-semibold mb-2 text-[var(--color-text-primary)]">{title || config.title}</h3>
            <p className="text-sm text-[var(--color-text-secondary)] max-w-sm leading-relaxed">
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
