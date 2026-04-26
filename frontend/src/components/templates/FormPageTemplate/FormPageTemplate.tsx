import type { ReactNode } from 'react';

interface FormPageTemplateProps {
    header: ReactNode;
    form: ReactNode;
    footer?: ReactNode;
}

export function FormPageTemplate({ header, form, footer }: FormPageTemplateProps) {
    return (
        <div className="flex min-h-full flex-col">
            <div className="flex-1">
                {header}
                <div className="p-8 bg-surface-card rounded-xl mt-6">{form}</div>
            </div>
            {footer && (
                <div className="sticky bottom-0 z-10 mt-6 flex items-center justify-end gap-3 bg-primary border-t border-border-default px-8 py-5">
                    {footer}
                </div>
            )}
        </div>
    );
}
