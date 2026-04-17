import { cn } from '~/utils/cn';

interface DateRangeShellProps {
    startLabel?: string;
    endLabel?: string;
    startValue?: string;
    endValue?: string;
    onStartChange?: (value: string) => void;
    onEndChange?: (value: string) => void;
    className?: string;
}

export function DateRangeShell({
    startLabel = 'From',
    endLabel = 'To',
    startValue,
    endValue,
    onStartChange,
    onEndChange,
    className,
}: DateRangeShellProps) {
    return (
        <div className={cn('flex items-end gap-3', className)}>
            <div className="flex flex-col gap-2">
                <label className="text-sm font-semibold text-[var(--color-text-primary)]">{startLabel}</label>
                <input
                    type="date"
                    value={startValue}
                    onChange={(e) => onStartChange?.(e.target.value)}
                    className="px-4 py-3 text-base bg-[var(--color-bg-primary)] border border-[var(--color-border-default)] rounded-lg outline-none focus:border-[var(--color-accent-indigo)] focus:ring-1 focus:ring-[var(--color-accent-indigo)]"
                />
            </div>
            <span className="pb-3 text-[var(--color-text-tertiary)]">&mdash;</span>
            <div className="flex flex-col gap-2">
                <label className="text-sm font-semibold text-[var(--color-text-primary)]">{endLabel}</label>
                <input
                    type="date"
                    value={endValue}
                    onChange={(e) => onEndChange?.(e.target.value)}
                    className="px-4 py-3 text-base bg-[var(--color-bg-primary)] border border-[var(--color-border-default)] rounded-lg outline-none focus:border-[var(--color-accent-indigo)] focus:ring-1 focus:ring-[var(--color-accent-indigo)]"
                />
            </div>
        </div>
    );
}
