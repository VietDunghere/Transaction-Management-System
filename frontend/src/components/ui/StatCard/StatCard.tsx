import { cn } from '~/utils/cn';

interface StatCardProps {
    label: string;
    value: string | number;
    change?: string;
    changeType?: 'positive' | 'negative' | 'neutral';
    accent?: 'purple' | 'blue';
}

export function StatCard({ label, value, change, changeType = 'neutral', accent = 'purple' }: StatCardProps) {
    return (
        <div
            className={cn(
                'flex flex-col gap-2 rounded-xl',
                accent === 'purple' ? 'bg-[var(--color-bg-accent-purple)]' : 'bg-[var(--color-bg-accent-blue)]',
            )}
            style={{ padding: 24 }}
        >
            <span className="text-base font-normal text-[var(--color-text-on-accent)]">{label}</span>
            <span className="text-2xl font-semibold leading-8 text-[var(--color-text-on-accent)]">{value}</span>
            {change && (
                <span
                    className={cn(
                        'text-sm',
                        changeType === 'positive' && 'text-emerald-600',
                        changeType === 'negative' && 'text-red-600',
                        changeType === 'neutral' && 'text-[var(--color-text-secondary)]',
                    )}
                >
                    {change}
                </span>
            )}
        </div>
    );
}
