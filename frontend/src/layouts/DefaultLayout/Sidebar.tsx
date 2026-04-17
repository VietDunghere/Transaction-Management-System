import {
    LayoutDashboard,
    ArrowLeftRight,
    ShieldAlert,
    BarChart3,
    Users,
    CreditCard,
    ScrollText,
    Database,
    User,
    ChevronRight,
    Component,
} from 'lucide-react';
import { Link, useRouterState } from '@tanstack/react-router';
import { cn } from '~/utils/cn';
import type { Role } from '~/types/api';
import { useAuthStore } from '~/stores/useAuthStore';

interface SidebarProps {
    isOpen: boolean;
    onToggle: () => void;
}

interface NavItem {
    label: string;
    icon: React.ReactNode;
    href: string;
    roles?: Role[];
}

const mainNavItems: NavItem[] = [
    { label: 'Dashboard', icon: <LayoutDashboard size={20} />, href: '/', roles: ['MANAGER', 'ADMIN'] },
    { label: 'Transactions', icon: <ArrowLeftRight size={20} />, href: '/transactions' },
    { label: 'Cases', icon: <ShieldAlert size={20} />, href: '/cases', roles: ['REVIEWER', 'MANAGER', 'ADMIN'] },
    { label: 'Users', icon: <Users size={20} />, href: '/users', roles: ['MANAGER', 'ADMIN'] },
    { label: 'Loans', icon: <CreditCard size={20} />, href: '/loans', roles: ['OPERATOR', 'MANAGER', 'ADMIN'] },
];

const secondaryNavItems: NavItem[] = [
    { label: 'Reports', icon: <BarChart3 size={20} />, href: '/reports', roles: ['MANAGER', 'ADMIN'] },
    { label: 'Audit Logs', icon: <ScrollText size={20} />, href: '/audit-logs', roles: ['MANAGER', 'ADMIN'] },
    { label: 'ETL Pipeline', icon: <Database size={20} />, href: '/etl', roles: ['ADMIN'] },
    { label: 'Profile', icon: <User size={20} />, href: '/profile' },
    { label: 'UI Demo', icon: <Component size={20} />, href: '/ui-demo' },
];

function filterByRole(items: NavItem[], role: Role | undefined): NavItem[] {
    if (!role) return [];
    return items.filter((item) => !item.roles || item.roles.includes(role));
}

export function Sidebar({ isOpen, onToggle }: SidebarProps) {
    const routerState = useRouterState();
    const currentPath = routerState.location.pathname;
    const user = useAuthStore((s) => s.user);
    const userRole = user?.role;

    const visibleMain = filterByRole(mainNavItems, userRole);
    const visibleSecondary = filterByRole(secondaryNavItems, userRole);

    const userInitial = user?.full_name?.charAt(0).toUpperCase() ?? '?';

    return (
        <>
            {/* Mobile overlay */}
            {isOpen && <div className="fixed inset-0 z-40 bg-black/20 md:hidden" onClick={onToggle} />}

            <aside
                className={cn(
                    'flex flex-col bg-primary',
                    'border-r border-[var(--color-border-default)]',
                    'transition-all duration-300',
                    'z-50 shrink-0',
                    'fixed inset-y-0 left-0 md:relative',
                    isOpen
                        ? 'w-[var(--sidebar-width)] translate-x-0'
                        : 'w-[var(--sidebar-collapsed)] -translate-x-full md:translate-x-0',
                )}
                style={{ padding: 16 }}
            >
                {/* User row */}
                <div className="flex items-center gap-3 px-2 py-2 mb-2">
                    <div className="flex size-6 shrink-0 items-center justify-center rounded-full bg-accent-purple">
                        <span className="text-[10px] font-semibold text-[var(--color-text-on-accent)]">
                            {userInitial}
                        </span>
                    </div>
                    {isOpen && (
                        <span className="text-sm font-normal text-[var(--color-text-primary)] truncate">
                            {user?.full_name ?? 'Loading...'}
                        </span>
                    )}
                </div>

                {/* Scrollable nav area */}
                <nav className="flex-1 overflow-y-auto">
                    {/* MAIN section */}
                    {isOpen && (
                        <div className="px-3 py-1 mb-1">
                            <span className="text-xs font-normal text-[var(--color-text-secondary)] uppercase tracking-wider">
                                Main
                            </span>
                        </div>
                    )}
                    <ul className="flex flex-col gap-0.5">
                        {visibleMain.map((item) => {
                            const isActive =
                                currentPath === item.href ||
                                (item.href !== '/' && currentPath.startsWith(item.href + '/'));
                            return (
                                <li key={item.href}>
                                    <Link
                                        to={item.href}
                                        className={cn(
                                            'flex items-center gap-2 px-2 py-2',
                                            'rounded-sm text-sm transition-colors duration-150',
                                            isActive
                                                ? 'text-[var(--color-text-primary)] font-semibold'
                                                : 'text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]',
                                        )}
                                    >
                                        <ChevronRight
                                            size={16}
                                            className="shrink-0 text-[var(--color-text-tertiary)]"
                                        />
                                        <span className="shrink-0">{item.icon}</span>
                                        {isOpen && <span className="truncate">{item.label}</span>}
                                    </Link>
                                </li>
                            );
                        })}
                    </ul>

                    {/* SECONDARY section */}
                    {isOpen && (
                        <div className="px-3 py-1 mt-4 mb-1">
                            <span className="text-xs font-normal text-[var(--color-text-secondary)] uppercase tracking-wider">
                                Management
                            </span>
                        </div>
                    )}
                    <ul className="flex flex-col gap-0.5">
                        {visibleSecondary.map((item) => {
                            const isActive = currentPath === item.href || currentPath.startsWith(item.href + '/');
                            return (
                                <li key={item.href}>
                                    <Link
                                        to={item.href}
                                        className={cn(
                                            'flex items-center gap-2 px-2 py-2',
                                            'rounded-sm text-sm transition-colors duration-150',
                                            isActive
                                                ? 'text-[var(--color-text-primary)] font-semibold'
                                                : 'text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]',
                                        )}
                                    >
                                        <ChevronRight
                                            size={16}
                                            className="shrink-0 text-[var(--color-text-tertiary)]"
                                        />
                                        <span className="shrink-0">{item.icon}</span>
                                        {isOpen && <span className="truncate">{item.label}</span>}
                                    </Link>
                                </li>
                            );
                        })}
                    </ul>
                </nav>

                {/* Footer — HuzaFraud logo */}
                {isOpen && (
                    <div className="flex items-center gap-2 px-2 py-2 mt-2">
                        <div className="flex size-5 items-center justify-center rounded-sm bg-accent-indigo">
                            <span className="text-[8px] font-semibold text-white">H</span>
                        </div>
                        <span className="text-xs text-[var(--color-text-secondary)]">HuzaFraud</span>
                    </div>
                )}
            </aside>
        </>
    );
}
