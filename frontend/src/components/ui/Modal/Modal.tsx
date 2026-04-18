import type { ReactNode } from 'react';
import { X } from 'lucide-react';
import { cn } from '~/utils/cn';

interface ModalProps {
    isOpen: boolean;
    onClose: () => void;
    title?: string;
    children: ReactNode;
    footer?: ReactNode;
    size?: 'sm' | 'md' | 'lg';
}

const sizeMap: Record<string, string> = {
    sm: '448px',
    md: '512px',
    lg: '672px',
};

export function Modal({ isOpen, onClose, title, children, footer, size = 'md' }: ModalProps) {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-black/30" onClick={onClose}>
            <div
                className="relative w-full flex flex-col bg-primary border border-border-default rounded-xl overflow-hidden"
                style={{ maxWidth: sizeMap[size], maxHeight: '85vh' }}
                onClick={(e) => e.stopPropagation()}
            >
                {title && (
                    <div className="flex items-center justify-between px-6 py-4 border-b border-border-default shrink-0">
                        <h2 className="text-base font-semibold">{title}</h2>
                        <button
                            onClick={onClose}
                            className={cn(
                                'flex items-center justify-center size-8',
                                'rounded-lg hover:bg-subtle transition-colors cursor-pointer',
                            )}
                            style={{ border: 'none', background: 'transparent' }}
                        >
                            <X size={18} />
                        </button>
                    </div>
                )}

                <div className="flex-1 overflow-y-auto p-6">{children}</div>

                {footer && (
                    <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-border-default shrink-0">
                        {footer}
                    </div>
                )}
            </div>
        </div>
    );
}
