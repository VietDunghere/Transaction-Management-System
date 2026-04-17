import { useState } from 'react';
import { Search, Bell, LogOut, User, Menu } from 'lucide-react';
import { Link, useRouterState } from '@tanstack/react-router';
import { cn } from '~/utils/cn';
import { useAuthStore } from '~/stores/useAuthStore';
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
    '/reports': 'Reports',
    '/etl': 'ETL Pipeline',
    '/profile': 'Profile',
    '/ui-demo': 'UI Demo',
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
    const logout = useLogout();
    const [userMenuOpen, setUserMenuOpen] = useState(false);
    const routerState = useRouterState();
    const breadcrumbs = getBreadcrumbs(routerState.location.pathname);

    return (
        <header
            className={cn(
                'flex items-center justify-between shrink-0',
                'bg-[var(--color-bg-primary)]',
                'border-b border-[var(--color-border-default)]',
            )}
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
                            {idx > 0 && <span className="text-xs text-[var(--color-text-tertiary)]">/</span>}
                            <span
                                className={cn(
                                    'text-xs px-2 py-1 rounded-sm',
                                    idx === breadcrumbs.length - 1
                                        ? 'text-[var(--color-text-primary)] font-medium'
                                        : 'text-[var(--color-text-secondary)]',
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
                    className="hidden sm:flex items-center gap-2 rounded-sm bg-[var(--color-surface-input)] cursor-pointer"
                    style={{ padding: '4px 8px', width: 160, height: 28 }}
                >
                    <Search size={14} className="text-[var(--color-text-tertiary)] shrink-0" />
                    <span className="flex-1 text-xs text-[var(--color-text-tertiary)]">Search</span>
                    <span className="text-xs text-[var(--color-text-tertiary)] bg-[var(--color-bg-primary)] px-1.5 py-0.5 rounded-sm border border-[var(--color-border-default)]">
                        /
                    </span>
                </div>

                {/* Notifications */}
                <button
                    className="flex items-center justify-center size-7 rounded-sm cursor-pointer hover:bg-[var(--color-bg-subtle)] transition-colors"
                    style={{ border: 'none', background: 'transparent' }}
                    aria-label="Notifications"
                >
                    <Bell size={16} className="text-[var(--color-text-primary)]" />
                </button>

                {/* User menu */}
                <div className="relative">
                    <button
                        onClick={() => setUserMenuOpen((o) => !o)}
                        className="flex items-center gap-2 px-2 py-1 rounded-sm cursor-pointer hover:bg-[var(--color-bg-subtle)] transition-colors"
                        style={{ border: 'none', background: 'transparent' }}
                    >
                        <div className="flex size-6 items-center justify-center rounded-full bg-[var(--color-bg-accent-purple)]">
                            <span className="text-[10px] font-semibold text-[var(--color-text-on-accent)]">
                                {user?.full_name?.charAt(0).toUpperCase() ?? '?'}
                            </span>
                        </div>
                        <span className="hidden sm:block text-xs text-[var(--color-text-primary)]">
                            {user?.full_name ?? 'User'}
                        </span>
                    </button>

                    {userMenuOpen && (
                        <>
                            <div className="fixed inset-0 z-40" onClick={() => setUserMenuOpen(false)} />
                            <div
                                className={cn(
                                    'absolute right-0 top-full mt-1 z-50',
                                    'bg-[var(--color-bg-primary)] border border-[var(--color-border-default)]',
                                    'rounded-sm shadow-lg min-w-[180px]',
                                )}
                            >
                                <div className="px-3 py-2 border-b border-[var(--color-border-default)]">
                                    <p className="text-xs font-medium text-[var(--color-text-primary)]">
                                        {user?.full_name}
                                    </p>
                                    <p className="text-xs text-[var(--color-text-secondary)]">{user?.role}</p>
                                </div>
                                <Link
                                    to="/profile"
                                    onClick={() => setUserMenuOpen(false)}
                                    className="flex items-center gap-2 px-3 py-2 text-xs text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-subtle)] transition-colors"
                                >
                                    <User size={14} /> Profile
                                </Link>
                                <button
                                    onClick={() => {
                                        setUserMenuOpen(false);
                                        logout.mutate();
                                    }}
                                    className="flex items-center gap-2 w-full px-3 py-2 text-xs text-[var(--color-status-danger)] hover:bg-[var(--color-bg-subtle)] transition-colors cursor-pointer"
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
