import type { ReactNode } from 'react';
import { cn } from '~/utils/cn';

const cardStyle: React.CSSProperties = {
    background: '#ffffff',
    border: '2px solid #1a1a1a',
    boxShadow: '4px 4px 0 0 #1a1a1a',
    borderRadius: '6px',
};

/* ============================================================
   PageHeader — Shared page title + action area
   ============================================================ */

interface PageHeaderProps {
    title: string;
    subtitle?: string;
    actions?: ReactNode;
}

export function PageHeader({ title, subtitle, actions }: PageHeaderProps) {
    return (
        <div className="mb-10 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div>
                <h1 className="text-3xl font-black leading-tight">
                    {title}
                </h1>
                {subtitle && (
                    <p className="mt-2 text-base text-[#525252]">
                        {subtitle}
                    </p>
                )}
            </div>
            {actions && <div className="flex items-center gap-3">{actions}</div>}
        </div>
    );
}

/* ============================================================
   ListPageTemplate — Filter bar + Table zone + Pagination
   ============================================================ */

interface ListPageTemplateProps {
    header: ReactNode;
    filterBar?: ReactNode;
    table: ReactNode;
    pagination?: ReactNode;
}

export function ListPageTemplate({ header, filterBar, table, pagination }: ListPageTemplateProps) {
    return (
        <div className="flex flex-col gap-6">
            {header}
            {filterBar && (
                <div style={{ ...cardStyle, padding: '2rem' }}>
                    {filterBar}
                </div>
            )}
            <div style={{ ...cardStyle, overflow: 'hidden' }}>
                {table}
            </div>
            {pagination && (
                <div className="flex justify-center">{pagination}</div>
            )}
        </div>
    );
}

/* ============================================================
   DetailPageTemplate — Summary + Info + Timeline/Activities
   ============================================================ */

interface DetailPageTemplateProps {
    header: ReactNode;
    summary: ReactNode;
    info: ReactNode;
    timeline?: ReactNode;
}

export function DetailPageTemplate({ header, summary, info, timeline }: DetailPageTemplateProps) {
    return (
        <div className="flex flex-col gap-6">
            {header}
            <div className={cn('grid gap-8', 'lg:grid-cols-3')}>
                <div style={{ ...cardStyle, padding: '2rem' }} className="lg:col-span-1">
                    {summary}
                </div>
                <div style={{ ...cardStyle, padding: '2rem' }} className="lg:col-span-2">
                    {info}
                </div>
            </div>
            {timeline && (
                <div style={{ ...cardStyle, padding: '2rem' }}>
                    {timeline}
                </div>
            )}
        </div>
    );
}

/* ============================================================
   DashboardTemplate — KPI row + Chart row + Secondary cards
   ============================================================ */

interface DashboardTemplateProps {
    header: ReactNode;
    kpiRow: ReactNode;
    chartRow: ReactNode;
    secondaryCards?: ReactNode;
}

export function DashboardTemplate({ header, kpiRow, chartRow, secondaryCards }: DashboardTemplateProps) {
    return (
        <div className="flex flex-col gap-6">
            {header}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                {kpiRow}
            </div>
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
                {chartRow}
            </div>
            {secondaryCards && (
                <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {secondaryCards}
                </div>
            )}
        </div>
    );
}

/* ============================================================
   FormPageTemplate — Form body + Sticky action footer
   ============================================================ */

interface FormPageTemplateProps {
    header: ReactNode;
    form: ReactNode;
    footer: ReactNode;
}

export function FormPageTemplate({ header, form, footer }: FormPageTemplateProps) {
    return (
        <div className="flex min-h-full flex-col">
            <div className="flex-1">
                {header}
                <div style={{ ...cardStyle, padding: '2.5rem', marginTop: '2rem' }}>
                    {form}
                </div>
            </div>
            {/* Sticky footer */}
            <div
                className="sticky bottom-0 z-10 mt-6 flex items-center justify-end gap-2"
                style={{
                    background: '#ffffff',
                    borderTop: '2px solid #1a1a1a',
                    padding: '1.5rem 2.5rem',
                }}
            >
                {footer}
            </div>
        </div>
    );
}
