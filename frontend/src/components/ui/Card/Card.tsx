import type { ReactNode, HTMLAttributes } from 'react';
import { cn } from '~/utils/cn';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
    children: ReactNode;
    hover?: boolean;
    noPadding?: boolean;
}

export function Card({ children, hover = false, noPadding = false, className, ...rest }: CardProps) {
    return (
        <div
            className={cn(
                'bg-surface-card rounded-xl',
                hover && 'cursor-pointer transition-colors duration-150 hover:bg-subtle',
                noPadding ? '' : 'p-8',
                className,
            )}
            {...rest}
        >
            {children}
        </div>
    );
}
