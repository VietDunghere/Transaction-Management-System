import { cn } from '~/utils/cn';

export type QuickPeriod = 'D' | 'W' | 'M';

const PERIODS: { value: QuickPeriod; label: string; title: string }[] = [
    { value: 'D', label: '1D', title: 'Hôm qua đến nay' },
    { value: 'W', label: '1W', title: '7 ngày gần đây' },
    { value: 'M', label: '1M', title: '30 ngày gần đây' },
];

interface QuickDateFilterProps {
    value: QuickPeriod | undefined;
    onChange: (period: QuickPeriod | undefined) => void;
}

export function QuickDateFilter({ value, onChange }: QuickDateFilterProps) {
    return (
        <div className="flex items-center gap-1">
            {PERIODS.map((p) => (
                <button
                    key={p.value}
                    title={p.title}
                    onClick={() => onChange(value === p.value ? undefined : p.value)}
                    className={cn(
                        'px-3 py-2 text-sm rounded-lg border transition-colors duration-150',
                        value === p.value
                            ? 'bg-accent-indigo text-text-on-accent border-accent-indigo font-semibold'
                            : 'bg-primary text-text-secondary border-border-default hover:text-text-primary hover:border-accent-indigo',
                    )}
                >
                    {p.label}
                </button>
            ))}
        </div>
    );
}
