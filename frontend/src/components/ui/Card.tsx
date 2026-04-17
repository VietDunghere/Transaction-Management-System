import type { ReactNode, HTMLAttributes } from 'react';
import { cn } from '~/utils/cn';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
    children: ReactNode;
    hover?: boolean;
    noPadding?: boolean;
}

export function Card({ children, hover = false, noPadding = false, className, style, ...rest }: CardProps) {
    return (
        <div
            className={cn(
                'bg-white rounded-md',
                hover && 'cursor-pointer transition-transform duration-150 hover:-translate-x-0.5 hover:-translate-y-0.5',
                className,
            )}
            style={{
                padding: noPadding ? '0' : '2.5rem',  /* Strong padding to balance content */
                border: '2px solid #1a1a1a',
                boxShadow: hover ? undefined : '4px 4px 0 0 #1a1a1a',
                ...(hover ? { '--hover-shadow': '6px 6px 0 0 #1a1a1a' } as React.CSSProperties : {}),
                ...style,
            }}
            {...rest}
        >
            {children}
        </div>
    );
}
