import { useState } from 'react';
import { Search, Bell, LogOut, User, Menu, Sun, Moon } from 'lucide-react';
import { Link, useRouterState } from '@tanstack/react-router';
import { cn } from '~/utils/cn';
import { useAuthStore } from '~/stores/useAuthStore';
import { useUIStore } from '~/stores/useUIStore';
import { useLogout } from '~/hooks/useAuth';

interface HeaderProps {
    isSidebarOpen: boolean;
    onToggleSidebar: () => void;
}

const breadcrumbMap: Record<string, string> = {
    '/': 'Dashboard',
    '/transactions': 'Transactions',
    '/transactions/submit': 'Submit Transaction',
    '/cases': 'Cases',
    '/users': 'Users',
    '/users/create': 'Create User',
    '/loans': 'Loans',
    '/loans/create': 'Create Loan',
    '/loans/simulate': 'Loan Simulator',
    '/audit-logs': 'Audit Logs',
    '/analyst/thresholds': 'Thresholds',
    '/analyst/model-performance': 'Model Performance',
    '/profile': 'Profile',
};

function getBreadcrumbs(pathname: string) {
    const label = breadcrumbMap[pathname];
    if (label) return [label];
    // Dynamic routes like /transactions/$txnId
    const segments = pathname.split('/').filter(Boolean);
    if (segments.length >= 2) {
        const parentPath = '/' + segments[0];
        const parentLabel = breadcrumbMap[parentPath];
        if (parentLabel) return [parentLabel, 'Detail'];
    }
    return ['Page'];
}

export function Header({ onToggleSidebar }: HeaderProps) {
    const user = useAuthStore((s) => s.user);
    const { theme, toggleTheme } = useUIStore();
    const logout = useLogout();
    const [userMenuOpen, setUserMenuOpen] = useState(false);
    const routerState = useRouterState();
    const breadcrumbs = getBreadcrumbs(routerState.location.pathname);

    return (
        <header
            className={cn('flex items-center justify-between shrink-0', 'bg-primary', 'border-b border-border-default')}
            style={{ height: 'var(--header-height)', padding: '20px 28px' }}
        >
            {/* Left — mobile toggle + breadcrumb */}
            <div className="flex items-center gap-2">
                <button
                    onClick={onToggleSidebar}
                    className="flex items-center justify-center size-6 rounded-sm md:hidden cursor-pointer"
                    style={{ border: 'none', background: 'transparent' }}
                    aria-label="Toggle sidebar"
                >
                    <Menu size={16} />
                </button>

                <nav className="flex items-center gap-1 ml-1" aria-label="Breadcrumb">
                    {breadcrumbs.map((crumb, idx) => (
                        <span key={idx} className="flex items-center gap-1">
                            {idx > 0 && <span className="text-xs text-text-tertiary">/</span>}
                            <span
                                className={cn(
                                    'text-xs px-2 py-1 rounded-sm',
                                    idx === breadcrumbs.length - 1
                                        ? 'text-text-primary font-medium'
                                        : 'text-text-secondary',
                                )}
                            >
                                {crumb}
                            </span>
                        </span>
                    ))}
                </nav>
            </div>

            {/* Right — search + notifications + user */}
            <div className="flex items-center gap-4">
                {/* Search box */}
                <div
                    className="hidden sm:flex items-center gap-2 rounded-sm bg-surface-input cursor-pointer"
                    style={{ padding: '4px 8px', width: 160, height: 28 }}
                >
                    <Search size={14} className="text-text-tertiary shrink-0" />
                    <span className="flex-1 text-xs text-text-tertiary">Search</span>
                    <span className="text-xs text-text-tertiary bg-primary px-1.5 py-0.5 rounded-sm border border-border-default">
                        /
                    </span>
                </div>

                {/* Theme toggle */}
                <button
                    onClick={toggleTheme}
                    className="flex items-center justify-center size-7 rounded-sm cursor-pointer hover:bg-subtle transition-colors"
                    style={{ border: 'none', background: 'transparent' }}
                    aria-label="Toggle theme"
                >
                    {theme === 'light' ? (
                        <Moon size={16} className="text-text-primary" />
                    ) : (
                        <Sun size={16} className="text-text-primary" />
                    )}
                </button>

                {/* Notifications */}
                <button
                    className="flex items-center justify-center size-7 rounded-sm cursor-pointer hover:bg-subtle transition-colors"
                    style={{ border: 'none', background: 'transparent' }}
                    aria-label="Notifications"
                >
                    <Bell size={16} className="text-text-primary" />
                </button>

                {/* User menu */}
                <div className="relative">
                    <button
                        onClick={() => setUserMenuOpen((o) => !o)}
                        className="flex items-center gap-2 px-2 py-1 rounded-sm cursor-pointer hover:bg-subtle transition-colors"
                        style={{ border: 'none', background: 'transparent' }}
                    >
                        <div className="flex size-6 items-center justify-center rounded-full bg-accent-purple">
                            <span className="text-[0.625rem] font-semibold text-text-on-accent">
                                {user?.full_name?.charAt(0).toUpperCase() ?? '?'}
                            </span>
                        </div>
                        <span className="hidden sm:block text-xs text-text-primary">{user?.full_name ?? 'User'}</span>
                    </button>

                    {userMenuOpen && (
                        <>
                            <div className="fixed inset-0 z-40" onClick={() => setUserMenuOpen(false)} />
                            <div
                                className={cn(
                                    'absolute right-0 top-full mt-1 z-50',
                                    'bg-primary border border-border-default',
                                    'rounded-sm shadow-lg min-w-45',
                                )}
                            >
                                <div className="px-3 py-2 border-b border-border-default">
                                    <p className="text-xs font-medium text-text-primary">{user?.full_name}</p>
                                    <p className="text-xs text-text-secondary">{user?.role}</p>
                                </div>
                                <Link
                                    to="/profile"
                                    onClick={() => setUserMenuOpen(false)}
                                    className="flex items-center gap-2 px-3 py-2 text-xs text-text-secondary hover:bg-subtle transition-colors"
                                >
                                    <User size={14} /> Profile
                                </Link>
                                <button
                                    onClick={() => {
                                        setUserMenuOpen(false);
                                        logout.mutate();
                                    }}
                                    className="flex items-center gap-2 w-full px-3 py-2 text-xs text-status-danger hover:bg-subtle transition-colors cursor-pointer"
                                    style={{ border: 'none', background: 'transparent' }}
                                >
                                    <LogOut size={14} /> Sign Out
                                </button>
                            </div>
                        </>
                    )}
                </div>
            </div>
        </header>
    );
}
