import { Menu, Bell, User } from 'lucide-react';
import { cn } from '~/utils/cn';

interface HeaderProps {
    isSidebarOpen: boolean;
    onToggleSidebar: () => void;
}

export function Header({ onToggleSidebar, isSidebarOpen: _isSidebarOpen }: HeaderProps) {
    return (
        <header
            className={cn(
                'flex items-center justify-between shrink-0',
                'px-6',
                'bg-white',
                'border-b-2 border-[#1a1a1a]',
            )}
            style={{ height: 'var(--header-height)' }}
        >
            {/* Left — Hamburger (visible on all sizes) + breadcrumb slot */}
            <div className="flex items-center gap-3">
                <button
                    id="sidebar-toggle-btn"
                    onClick={onToggleSidebar}
                    className={cn(
                        'flex items-center justify-center',
                        'size-9 rounded-sm',
                        'hover:bg-[#f5f5f0]',
                        'transition-colors duration-150',
                        'cursor-pointer',
                    )}
                    aria-label="Toggle sidebar"
                    style={{ border: 'none', background: 'transparent' }}
                >
                    <Menu size={20} />
                </button>

                {/* Breadcrumb slot — injected by page later */}
                <div
                    id="header-breadcrumb"
                    className="text-sm text-[#a3a3a3]"
                />
            </div>

            {/* Right — Actions */}
            <div className="flex items-center gap-2">
                {/* Notifications */}
                <button
                    id="notification-btn"
                    className={cn(
                        'relative flex items-center justify-center',
                        'size-9 rounded-sm',
                        'hover:bg-[#f5f5f0]',
                        'transition-colors duration-150',
                        'cursor-pointer',
                    )}
                    style={{ border: 'none', background: 'transparent' }}
                    aria-label="Notifications"
                >
                    <Bell size={18} />
                    <span
                        className="absolute top-1.5 right-1.5 size-2 rounded-full bg-[#ef4444]"
                        aria-hidden
                    />
                </button>

                {/* User avatar */}
                <button
                    id="user-profile-btn"
                    className={cn(
                        'flex items-center gap-2',
                        'px-3 py-1',
                        'rounded-sm',
                        'border-2 border-[#1a1a1a]',
                        'bg-white',
                        'hover:bg-[#f5f5f0]',
                        'text-sm font-medium',
                        'transition-all duration-150',
                        'cursor-pointer',
                    )}
                    style={{ boxShadow: 'var(--shadow-brutal-sm)' }}
                >
                    <User size={16} />
                    <span className="hidden sm:inline">Admin</span>
                </button>
            </div>
        </header>
    );
}
