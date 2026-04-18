import type { ReactNode } from 'react';
import { cn } from '~/utils/cn';

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
                    <tr className="border-b border-border-default">
                        {columns.map((col) => (
                            <th
                                key={col.key}
                                className={cn(
                                    'px-6 py-4',
                                    'text-sm font-semibold',
                                    'text-text-secondary uppercase tracking-wider',
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
                                'border-b border-border-default',
                                'transition-colors duration-150',
                                'hover:bg-subtle',
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
