import type { ReactNode } from 'react';
import { cn } from '~/utils/cn';

/* ============================================================
   TableShell — Presentational table wrapper
   ============================================================ */

interface TableColumn {
    key: string;
    label: string;
    width?: string;
    align?: 'left' | 'center' | 'right';
}

interface TableShellProps {
    columns: TableColumn[];
    data: Record<string, ReactNode>[];
    onRowClick?: (row: Record<string, ReactNode>, index: number) => void;
    className?: string;
}

export function TableShell({ columns, data, onRowClick, className }: TableShellProps) {
    return (
        <div className={cn('overflow-x-auto', className)}>
            <table className="w-full border-collapse text-base">
                <thead>
                    <tr className="border-b-2 border-[#1a1a1a] bg-[#f5f5f0]">
                        {columns.map((col) => (
                            <th
                                key={col.key}
                                className={cn(
                                    'px-6 py-4',
                                    'text-base font-bold',
                                    'text-[#525252] uppercase tracking-wider',
                                    col.align === 'center' && 'text-center',
                                    col.align === 'right' && 'text-right',
                                    !col.align && 'text-left',
                                )}
                                style={col.width ? { width: col.width } : undefined}
                            >
                                {col.label}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {data.map((row, idx) => (
                        <tr
                            key={idx}
                            className={cn(
                                'border-b border-[#d4d4d4]',
                                'transition-colors duration-150',
                                'hover:bg-[#f5f5f0]',
                                onRowClick && 'cursor-pointer',
                            )}
                            onClick={() => onRowClick?.(row, idx)}
                        >
                            {columns.map((col) => (
                                <td
                                    key={col.key}
                                    className={cn(
                                        'px-6 py-4',
                                        col.align === 'center' && 'text-center',
                                        col.align === 'right' && 'text-right',
                                    )}
                                >
                                    {row[col.key]}
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

/* ============================================================
   StatCard — KPI display card
   ============================================================ */

interface StatCardProps {
    label: string;
    value: string | number;
    change?: string;
    changeType?: 'positive' | 'negative' | 'neutral';
    icon?: ReactNode;
}

export function StatCard({ label, value, change, changeType = 'neutral', icon }: StatCardProps) {
    return (
        <div
            className="p-8 cursor-pointer transition-transform duration-150 hover:-translate-x-0.5 hover:-translate-y-0.5"
            style={{
                background: '#ffffff',
                border: '2px solid #1a1a1a',
                boxShadow: '4px 4px 0 0 #1a1a1a',
                borderRadius: '8px',
            }}
        >
            <div className="flex items-start justify-between">
                <div className="flex flex-col gap-2">
                    <span className="text-base font-bold text-[#525252] uppercase tracking-wider">
                        {label}
                    </span>
                    <span className="text-4xl font-black leading-none">
                        {value}
                    </span>
                    {change && (
                        <span
                            className={cn(
                                'text-sm font-bold mt-1',
                                changeType === 'positive' && 'text-[var(--color-accent-green)]',
                                changeType === 'negative' && 'text-[#ef4444]',
                                changeType === 'neutral' && 'text-[#a3a3a3]',
                            )}
                        >
                            {change}
                        </span>
                    )}
                </div>
                {icon && (
                    <div className="flex size-10 items-center justify-center rounded-sm bg-[#f5f5f0] text-[#525252]">
                        {icon}
                    </div>
                )}
            </div>
        </div>
    );
}

/* ============================================================
   KeyValueRow — Single row label-value display
   ============================================================ */

interface KeyValueRowProps {
    label: string;
    value: ReactNode;
    className?: string;
}

export function KeyValueRow({ label, value, className }: KeyValueRowProps) {
    return (
        <div className={cn('flex items-start justify-between py-4 border-b border-[#d4d4d4] last:border-b-0', className)}>
            <span className="text-base font-bold text-[#525252] shrink-0 mr-6">
                {label}
            </span>
            <span className="text-lg text-right">{value}</span>
        </div>
    );
}

/* ============================================================
   TimelineItem — Single timeline entry
   ============================================================ */

interface TimelineItemProps {
    title: string;
    description?: string;
    timestamp: string;
    icon?: ReactNode;
    variant?: 'default' | 'success' | 'warning' | 'danger';
}

const timelineDotStyles = {
    default: 'bg-[#1a1a1a]',
    success: 'bg-[var(--color-accent-green)]',
    warning: 'bg-[var(--color-accent-yellow)]',
    danger: 'bg-[#ef4444]',
};

export function TimelineItem({ title, description, timestamp, icon, variant = 'default' }: TimelineItemProps) {
    return (
        <div className="relative flex gap-6 pb-8 last:pb-0">
            {/* Line */}
            <div className="flex flex-col items-center">
                <div
                    className={cn(
                        'flex size-10 shrink-0 items-center justify-center rounded-full',
                        'border-2 border-[#1a1a1a]',
                        timelineDotStyles[variant],
                        variant === 'default' ? 'text-white' : 'text-white',
                    )}
                >
                    {icon || <span className="size-2 rounded-full bg-current" />}
                </div>
                <div className="w-0.5 flex-1 bg-[#d4d4d4]" />
            </div>
            {/* Content */}
            <div className="flex-1 pt-1">
                <p className="text-lg font-bold">{title}</p>
                {description && (
                    <p className="mt-1 text-base text-[#525252]">
                        {description}
                    </p>
                )}
                <p className="mt-1 text-sm text-[#a3a3a3]">
                    {timestamp}
                </p>
            </div>
        </div>
    );
}

/* ============================================================
   SectionHeader — Section title with optional action
   ============================================================ */

interface SectionHeaderProps {
    title: string;
    action?: ReactNode;
    className?: string;
}

export function SectionHeader({ title, action, className }: SectionHeaderProps) {
    return (
        <div className={cn('flex items-center justify-between mb-8', className)}>
            <h3 className="text-2xl font-black">{title}</h3>
            {action}
        </div>
    );
}
