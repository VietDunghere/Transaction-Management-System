import type { ReactNode } from 'react';

interface DetailPageTemplateProps {
    header: ReactNode;
    /** Full-width contextual alert/anomaly banner below the header */
    alertBanner?: ReactNode;
    /** Horizontal stat strip — rendered in a responsive 2/4-col grid */
    statBar?: ReactNode;
    /** Content split — main (2/3) + aside (1/3), or full width if no aside */
    main?: ReactNode;
    aside?: ReactNode;
    /** Full-width sections at the bottom (tables, timelines, etc.) */
    fullWidth?: ReactNode;
}

export function DetailPageTemplate({ header, alertBanner, statBar, main, aside, fullWidth }: DetailPageTemplateProps) {
    return (
        <div className="flex flex-col gap-6">
            {header}

            {alertBanner}

            {statBar && <div className="grid grid-cols-2 md:grid-cols-4 gap-4">{statBar}</div>}

            {(main || aside) && (
                <div className="grid gap-6 lg:grid-cols-3">
                    <div className={aside ? 'lg:col-span-2 flex flex-col gap-6' : 'lg:col-span-3 flex flex-col gap-6'}>
                        {main}
                    </div>
                    {aside && <div className="lg:col-span-1 flex flex-col gap-6">{aside}</div>}
                </div>
            )}

            {fullWidth && <div className="flex flex-col gap-6">{fullWidth}</div>}
        </div>
    );
}
