import type { ReactNode } from 'react';
import { Search, Calendar, ChevronLeft, ChevronRight } from 'lucide-react';
import { cn } from '~/utils/cn';

/* ============================================================
   SearchBox — Search input with icon
   ============================================================ */

interface SearchBoxProps {
    value?: string;
    onChange?: (value: string) => void;
    placeholder?: string;
    className?: string;
}

export function SearchBox({ value, onChange, placeholder = 'Search...', className }: SearchBoxProps) {
    return (
        <div className={cn('relative', className)}>
            <Search
                size={18}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-[#a3a3a3]"
            />
            <input
                type="text"
                value={value}
                onChange={(e) => onChange?.(e.target.value)}
                placeholder={placeholder}
                className={cn(
                    'w-full pl-10 pr-3 py-3',
                    'text-base',
                    'bg-white brutal-border',
                    'rounded-sm',
                    'outline-none transition-all duration-150',
                    'focus:ring-2 focus:ring-[#1a1a1a] focus:ring-offset-1',
                    'placeholder:text-[#a3a3a3]',
                )}
            />
        </div>
    );
}

/* ============================================================
   FilterBar — Horizontal filter container
   ============================================================ */

interface FilterBarProps {
    children: ReactNode;
    className?: string;
}

export function FilterBar({ children, className }: FilterBarProps) {
    return (
        <div
            className={cn(
                'flex flex-wrap items-end gap-3',
                className,
            )}
        >
            {children}
        </div>
    );
}

/* ============================================================
   DateRangeShell — Date range picker UI shell
   ============================================================ */

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
        <div className={cn('flex items-end gap-2', className)}>
            <div className="flex flex-col gap-1">
                <label className="text-base font-bold text-[#1a1a1a]">
                    {startLabel}
                </label>
                <div className="relative">
                    <input
                        type="date"
                        value={startValue}
                        onChange={(e) => onStartChange?.(e.target.value)}
                        className={cn(
                            'px-4 pr-3 py-3',
                            'text-base',
                            'bg-white brutal-border rounded-sm',
                            'outline-none focus:ring-2 focus:ring-[#1a1a1a] focus:ring-offset-1',
                        )}
                    />
                </div>
            </div>
            <span className="pb-2 text-[#a3a3a3]">—</span>
            <div className="flex flex-col gap-1">
                <label className="text-base font-bold text-[#1a1a1a]">
                    {endLabel}
                </label>
                <div className="relative">
                    <input
                        type="date"
                        value={endValue}
                        onChange={(e) => onEndChange?.(e.target.value)}
                        className={cn(
                            'px-4 pr-3 py-3',
                            'text-base',
                            'bg-white brutal-border rounded-sm',
                            'outline-none focus:ring-2 focus:ring-[#1a1a1a] focus:ring-offset-1',
                        )}
                    />
                </div>
            </div>
        </div>
    );
}

/* ============================================================
   Pagination — Page navigation control
   ============================================================ */

interface PaginationProps {
    currentPage: number;
    totalPages: number;
    onPageChange?: (page: number) => void;
}

export function Pagination({ currentPage, totalPages, onPageChange }: PaginationProps) {
    const pages = Array.from({ length: totalPages }, (_, i) => i + 1);

    // Show limited page numbers for large page counts
    const visiblePages = pages.filter((page) => {
        if (totalPages <= 7) return true;
        if (page === 1 || page === totalPages) return true;
        if (Math.abs(page - currentPage) <= 1) return true;
        return false;
    });

    return (
        <div className="flex items-center gap-1">
            <button
                onClick={() => onPageChange?.(currentPage - 1)}
                disabled={currentPage <= 1}
                className={cn(
                    'flex items-center justify-center size-10',
                    'rounded-sm brutal-border',
                    'text-base font-medium',
                    'hover:bg-[#f5f5f0] transition-colors',
                    currentPage <= 1 && 'opacity-50 pointer-events-none',
                )}
            >
                <ChevronLeft size={14} />
            </button>

            {visiblePages.map((page, idx) => {
                // Check for gap
                const prevPage = visiblePages[idx - 1];
                const hasGap = prevPage !== undefined && page - prevPage > 1;

                return (
                    <span key={page} className="contents">
                        {hasGap && (
                            <span className="flex items-center justify-center size-8 text-sm text-[#a3a3a3]">
                                ...
                            </span>
                        )}
                        <button
                            onClick={() => onPageChange?.(page)}
                            className={cn(
                                'flex items-center justify-center size-10',
                                'rounded-sm brutal-border',
                                'text-base font-medium',
                                'transition-colors',
                                page === currentPage
                                    ? 'bg-[#1a1a1a] text-white'
                                    : 'hover:bg-[#f5f5f0]',
                            )}
                        >
                            {page}
                        </button>
                    </span>
                );
            })}

            <button
                onClick={() => onPageChange?.(currentPage + 1)}
                disabled={currentPage >= totalPages}
                className={cn(
                    'flex items-center justify-center size-10',
                    'rounded-sm brutal-border',
                    'text-base font-medium',
                    'hover:bg-[#f5f5f0] transition-colors',
                    currentPage >= totalPages && 'opacity-50 pointer-events-none',
                )}
            >
                <ChevronRight size={14} />
            </button>
        </div>
    );
}
