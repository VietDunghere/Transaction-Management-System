import { ChevronLeft, ChevronRight, Search, Star, Bell, Clock, Settings, Menu } from 'lucide-react';
import { cn } from '~/utils/cn';

interface HeaderProps {
    isSidebarOpen: boolean;
    onToggleSidebar: () => void;
}

export function Header({ onToggleSidebar }: HeaderProps) {
    return (
        <header
            className={cn(
                'flex items-center justify-between shrink-0',
                'bg-[var(--color-bg-primary)]',
                'border-b border-[var(--color-border-default)]',
            )}
            style={{ height: 'var(--header-height)', padding: '20px 28px' }}
        >
            {/* Left — nav arrows + breadcrumb */}
            <div className="flex items-center gap-2">
                {/* Mobile menu toggle */}
                <button
                    onClick={onToggleSidebar}
                    className="flex items-center justify-center size-6 rounded-sm md:hidden cursor-pointer"
                    style={{ border: 'none', background: 'transparent' }}
                    aria-label="Toggle sidebar"
                >
                    <Menu size={16} />
                </button>

                {/* Nav arrows */}
                <button
                    className="flex items-center justify-center size-6 rounded-sm cursor-pointer hover:bg-[var(--color-bg-subtle)] transition-colors"
                    style={{ border: 'none', background: 'transparent', padding: 4 }}
                    aria-label="Go back"
                >
                    <ChevronLeft size={16} className="text-[var(--color-text-primary)]" />
                </button>
                <button
                    className="flex items-center justify-center size-6 rounded-sm cursor-pointer hover:bg-[var(--color-bg-subtle)] transition-colors"
                    style={{ border: 'none', background: 'transparent', padding: 4 }}
                    aria-label="Go forward"
                >
                    <ChevronRight size={16} className="text-[var(--color-text-primary)]" />
                </button>

                {/* Breadcrumb */}
                <nav className="flex items-center gap-2 ml-2" aria-label="Breadcrumb">
                    <span className="text-xs text-[var(--color-text-secondary)] px-3 py-1 rounded-sm cursor-pointer hover:bg-[var(--color-bg-subtle)] transition-colors">
                        Dashboards
                    </span>
                    <span className="text-xs text-[var(--color-text-tertiary)]">/</span>
                    <span className="text-xs text-[var(--color-text-secondary)] px-3 py-1 rounded-sm">Default</span>
                </nav>
            </div>

            {/* Right — search + action icons */}
            <div className="flex items-center gap-5">
                {/* Search box */}
                <div
                    className="hidden sm:flex items-center gap-2 rounded-sm bg-[var(--color-surface-input)] cursor-pointer"
                    style={{ padding: '4px 8px', width: 160, height: 28 }}
                >
                    <Search size={14} className="text-[var(--color-text-tertiary)] shrink-0" />
                    <span className="flex-1 text-xs text-[var(--color-text-tertiary)]">Search</span>
                    <span className="text-xs text-[var(--color-text-tertiary)] bg-[var(--color-bg-primary)] px-1.5 py-0.5 rounded-sm border border-[var(--color-border-default)]">
                        /
                    </span>
                </div>

                {/* Action icons */}
                <div className="flex items-center gap-1">
                    {[
                        { icon: <Star size={16} />, label: 'Favorites' },
                        { icon: <Bell size={16} />, label: 'Notifications' },
                        { icon: <Clock size={16} />, label: 'Recent' },
                        { icon: <Settings size={16} />, label: 'Settings' },
                    ].map((action) => (
                        <button
                            key={action.label}
                            className="flex items-center justify-center size-6 rounded-sm cursor-pointer hover:bg-[var(--color-bg-subtle)] transition-colors"
                            style={{ border: 'none', background: 'transparent', padding: 4 }}
                            aria-label={action.label}
                        >
                            <span className="text-[var(--color-text-primary)]">{action.icon}</span>
                        </button>
                    ))}
                </div>
            </div>
        </header>
    );
}
