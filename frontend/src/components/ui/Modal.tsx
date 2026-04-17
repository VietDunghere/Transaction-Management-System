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
        /* Overlay — full screen, flex centered */
        <div
            style={{ position: 'fixed', inset: 0, zIndex: 200, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '16px', background: 'rgba(0,0,0,0.5)' }}
            onClick={onClose}
        >
            {/* Modal box — stop propagation so clicking inside doesn't close */}
            <div
                style={{
                    position: 'relative',
                    width: '100%',
                    maxWidth: sizeMap[size],
                    maxHeight: '85vh',
                    display: 'flex',
                    flexDirection: 'column',
                    background: '#ffffff',
                    border: '2px solid #1a1a1a',
                    borderRadius: '6px',
                    boxShadow: '6px 6px 0 0 #1a1a1a',
                    overflow: 'hidden',
                }}
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header */}
                {title && (
                    <div
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            padding: '16px 24px',
                            borderBottom: '2px solid #1a1a1a',
                            flexShrink: 0,
                        }}
                    >
                        <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: 0 }}>{title}</h2>
                        <button
                            onClick={onClose}
                            className={cn(
                                'flex items-center justify-center size-8',
                                'rounded hover:bg-neutral-100 transition-colors cursor-pointer',
                            )}
                            style={{ border: 'none', background: 'transparent' }}
                        >
                            <X size={18} />
                        </button>
                    </div>
                )}

                {/* Body */}
                <div style={{ flex: '1 1 auto', overflowY: 'auto', padding: '24px' }}>
                    {children}
                </div>

                {/* Footer */}
                {footer && (
                    <div
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'flex-end',
                            gap: '8px',
                            padding: '16px 24px',
                            borderTop: '2px solid #1a1a1a',
                            flexShrink: 0,
                        }}
                    >
                        {footer}
                    </div>
                )}
            </div>
        </div>
    );
}
