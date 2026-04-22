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
    Component,
    SlidersHorizontal,
    Activity,
    ShieldOff,
    FileText,
    Layers,
    GitCompare,
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
    { label: 'Dashboard', icon: <LayoutDashboard size={20} />, href: '/', roles: ['ANALYST', 'MANAGER', 'ADMIN'] },
    {
        label: 'Transactions',
        icon: <ArrowLeftRight size={20} />,
        href: '/transactions',
        roles: ['ANALYST', 'MANAGER', 'ADMIN'],
    },
    { label: 'Cases', icon: <ShieldAlert size={20} />, href: '/cases', roles: ['REVIEWER', 'MANAGER', 'ADMIN'] },
    {
        label: 'Loans',
        icon: <CreditCard size={20} />,
        href: '/loans',
        roles: ['OPERATOR', 'REVIEWER', 'MANAGER', 'ADMIN'],
    },
    { label: 'Users', icon: <Users size={20} />, href: '/users', roles: ['MANAGER', 'ADMIN'] },
];

const analystNavItems: NavItem[] = [
    {
        label: 'Thresholds',
        icon: <SlidersHorizontal size={20} />,
        href: '/analyst/thresholds',
        roles: ['ANALYST', 'MANAGER', 'ADMIN'],
    },
    {
        label: 'Model Performance',
        icon: <Activity size={20} />,
        href: '/analyst/model-performance',
        roles: ['ANALYST', 'MANAGER', 'ADMIN'],
    },
    {
        label: 'Suppression Rules',
        icon: <ShieldOff size={20} />,
        href: '/analyst/suppression-rules',
        roles: ['ANALYST', 'ADMIN'],
    },
    {
        label: 'Analyst Reports',
        icon: <FileText size={20} />,
        href: '/analyst/reports',
        roles: ['ANALYST', 'MANAGER', 'ADMIN'],
    },
];

const secondaryNavItems: NavItem[] = [
    { label: 'Reports', icon: <BarChart3 size={20} />, href: '/reports', roles: ['MANAGER', 'ADMIN'] },
    { label: 'Audit Logs', icon: <ScrollText size={20} />, href: '/audit-logs', roles: ['MANAGER', 'ADMIN'] },
    { label: 'ETL Pipeline', icon: <Database size={20} />, href: '/etl', roles: ['ADMIN'] },
    { label: 'Data Lake', icon: <Layers size={20} />, href: '/datalake', roles: ['ADMIN'] },
    { label: 'Reconciliation', icon: <GitCompare size={20} />, href: '/reconciliation', roles: ['ADMIN'] },
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
    const visibleAnalyst = filterByRole(analystNavItems, userRole);
    const visibleSecondary = filterByRole(secondaryNavItems, userRole);

    const userInitial = user?.full_name?.charAt(0).toUpperCase() ?? '?';

    return (
        <>
            {/* Mobile overlay */}
            {isOpen && <div className="fixed inset-0 z-40 bg-black/20 md:hidden" onClick={onToggle} />}

            <aside
                className={cn(
                    'flex flex-col bg-primary',
                    'border-r border-border-default',
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
                        <span className="text-[0.625rem] font-semibold text-text-on-accent">{userInitial}</span>
                    </div>
                    {isOpen && (
                        <span className="text-sm font-normal text-text-primary truncate">
                            {user?.full_name ?? 'Loading...'}
                        </span>
                    )}
                </div>

                {/* Scrollable nav area */}
                <nav className="flex-1 overflow-y-auto">
                    {/* MAIN section */}
                    {isOpen && (
                        <div className="px-3 py-1 mb-1">
                            <span className="text-xs font-normal text-text-secondary uppercase tracking-wider">
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
                                            'flex items-center gap-2 px-5 py-2',
                                            'rounded-sm text-sm transition-colors duration-150',
                                            isActive
                                                ? 'text-text-primary font-semibold'
                                                : 'text-text-secondary hover:text-text-primary',
                                        )}
                                    >
                                        <span className="shrink-0">{item.icon}</span>
                                        {isOpen && <span className="truncate">{item.label}</span>}
                                    </Link>
                                </li>
                            );
                        })}
                    </ul>

                    {/* ANALYST section */}
                    {visibleAnalyst.length > 0 && (
                        <>
                            {isOpen && (
                                <div className="px-3 py-1 mt-4 mb-1">
                                    <span className="text-xs font-normal text-text-secondary uppercase tracking-wider">
                                        Analyst
                                    </span>
                                </div>
                            )}
                            <ul className="flex flex-col gap-0.5">
                                {visibleAnalyst.map((item) => {
                                    const isActive =
                                        currentPath === item.href || currentPath.startsWith(item.href + '/');
                                    return (
                                        <li key={item.href}>
                                            <Link
                                                to={item.href}
                                                className={cn(
                                                    'flex items-center gap-2 px-5 py-2',
                                                    'rounded-sm text-sm transition-colors duration-150',
                                                    isActive
                                                        ? 'text-text-primary font-semibold'
                                                        : 'text-text-secondary hover:text-text-primary',
                                                )}
                                            >
                                                <span className="shrink-0">{item.icon}</span>
                                                {isOpen && <span className="truncate">{item.label}</span>}
                                            </Link>
                                        </li>
                                    );
                                })}
                            </ul>
                        </>
                    )}

                    {/* SECONDARY section */}
                    {isOpen && (
                        <div className="px-3 py-1 mt-4 mb-1">
                            <span className="text-xs font-normal text-text-secondary uppercase tracking-wider">
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
                                            'flex items-center gap-2 px-5 py-2',
                                            'rounded-sm text-sm transition-colors duration-150',
                                            isActive
                                                ? 'text-text-primary font-semibold'
                                                : 'text-text-secondary hover:text-text-primary',
                                        )}
                                    >
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
                            <span className="text-[0.5rem] font-semibold text-white">H</span>
                        </div>
                        <span className="text-xs text-text-secondary">HuzaFraud</span>
                    </div>
                )}
            </aside>
        </>
    );
}
