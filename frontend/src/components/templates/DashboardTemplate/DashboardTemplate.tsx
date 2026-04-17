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
            {kpiRow}
            {chartRow}
            {secondaryCards}
        </div>
    );
}
