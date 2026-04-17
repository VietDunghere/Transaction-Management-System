import { ChevronLeft, ChevronRight } from 'lucide-react';
import { cn } from '~/utils/cn';

interface PaginationProps {
    currentPage: number;
    totalPages: number;
    onPageChange?: (page: number) => void;
}

export function Pagination({ currentPage, totalPages, onPageChange }: PaginationProps) {
    const pages = Array.from({ length: totalPages }, (_, i) => i + 1);

    const visiblePages = pages.filter((page) => {
        if (totalPages <= 7) return true;
        if (page === 1 || page === totalPages) return true;
        if (Math.abs(page - currentPage) <= 1) return true;
        return false;
    });

    return (
        <div className="flex items-center gap-1.5">
            <button
                onClick={() => onPageChange?.(currentPage - 1)}
                disabled={currentPage <= 1}
                className={cn(
                    'flex items-center justify-center size-10',
                    'rounded-lg border border-[var(--color-border-default)]',
                    'text-base',
                    'hover:bg-subtle transition-colors cursor-pointer',
                    currentPage <= 1 && 'opacity-50 pointer-events-none',
                )}
            >
                <ChevronLeft size={16} />
            </button>

            {visiblePages.map((page, idx) => {
                const prevPage = visiblePages[idx - 1];
                const hasGap = prevPage !== undefined && page - prevPage > 1;

                return (
                    <span key={page} className="contents">
                        {hasGap && (
                            <span className="flex items-center justify-center size-10 text-sm text-[var(--color-text-tertiary)]">
                                ...
                            </span>
                        )}
                        <button
                            onClick={() => onPageChange?.(page)}
                            className={cn(
                                'flex items-center justify-center size-10',
                                'rounded-lg',
                                'text-base cursor-pointer',
                                'transition-colors',
                                page === currentPage
                                    ? 'bg-text-primary text-[var(--color-bg-primary)]'
                                    : 'border border-[var(--color-border-default)] hover:bg-subtle',
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
                    'rounded-lg border border-[var(--color-border-default)]',
                    'text-base',
                    'hover:bg-subtle transition-colors cursor-pointer',
                    currentPage >= totalPages && 'opacity-50 pointer-events-none',
                )}
            >
                <ChevronRight size={16} />
            </button>
        </div>
    );
}
