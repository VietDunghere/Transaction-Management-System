import type { ReactNode } from 'react';
import { cn } from '~/utils/cn';

interface DetailPageTemplateProps {
    header: ReactNode;
    summary?: ReactNode;
    info: ReactNode;
    timeline?: ReactNode;
}

export function DetailPageTemplate({ header, summary, info, timeline }: DetailPageTemplateProps) {
    return (
        <div className="flex flex-col gap-6">
            {header}
            <div className={cn('grid gap-6', 'lg:grid-cols-3')}>
                {summary && (
                    <div className="p-8 bg-[var(--color-surface-card)] rounded-xl lg:col-span-1">{summary}</div>
                )}
                <div className={cn('p-8 bg-[var(--color-surface-card)] rounded-xl', summary ? 'lg:col-span-2' : 'lg:col-span-3')}>{info}</div>
            </div>
            {timeline && <div className="p-8 bg-[var(--color-surface-card)] rounded-xl">{timeline}</div>}
        </div>
    );
}
