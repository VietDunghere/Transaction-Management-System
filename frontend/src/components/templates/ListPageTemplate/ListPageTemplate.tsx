import type { ReactNode } from 'react';

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
            {filterBar && <div className="p-6 bg-surface-card rounded-xl">{filterBar}</div>}
            <div className="bg-surface-card rounded-xl overflow-hidden">{table}</div>
            {pagination && <div className="flex justify-center">{pagination}</div>}
        </div>
    );
}
