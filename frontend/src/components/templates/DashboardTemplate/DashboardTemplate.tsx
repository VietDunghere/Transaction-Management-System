import type { ReactNode } from 'react';

interface DashboardTemplateProps {
    header: ReactNode;
    kpiRow: ReactNode;
    chartRow: ReactNode;
    secondaryCards?: ReactNode;
}

export function DashboardTemplate({ header, kpiRow, chartRow, secondaryCards }: DashboardTemplateProps) {
    return (
        <div className="flex flex-col gap-7">
            {header}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">{kpiRow}</div>
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">{chartRow}</div>
            {secondaryCards && (
                <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">{secondaryCards}</div>
            )}
        </div>
    );
}
