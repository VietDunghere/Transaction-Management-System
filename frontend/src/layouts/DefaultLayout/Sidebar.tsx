import {
    LayoutDashboard,
    ArrowLeftRight,
    ShieldAlert,
    Users,
    CreditCard,
    ScrollText,
    User,
    SlidersHorizontal,
    Activity,
    Play,
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
    { label: 'Dashboard', icon: <LayoutDashboard size={20} />, href: '/', roles: ['ANALYST', 'MANAGER'] },
    {
        label: 'Transactions',
        icon: <ArrowLeftRight size={20} />,
        href: '/transactions',
        roles: ['ANALYST', 'MANAGER'],
    },
    { label: 'Cases', icon: <ShieldAlert size={20} />, href: '/cases', roles: ['REVIEWER'] },
    {
        label: 'Loans',
        icon: <CreditCard size={20} />,
        href: '/loans',
        roles: ['OPERATOR', 'REVIEWER'],
    },
    { label: 'Users', icon: <Users size={20} />, href: '/users', roles: ['MANAGER', 'ADMIN'] },
    { label: 'Demo Runner', icon: <Play size={20} />, href: '/demo', roles: ['OPERATOR'] },
];

const analystNavItems: NavItem[] = [
    {
        label: 'Thresholds',
        icon: <SlidersHorizontal size={20} />,
        href: '/analyst/thresholds',
        roles: ['ANALYST'],
    },
    {
        label: 'Model Performance',
        icon: <Activity size={20} />,
        href: '/analyst/model-performance',
        roles: ['ANALYST'],
    },
];

const secondaryNavItems: NavItem[] = [
    { label: 'Audit Logs', icon: <ScrollText size={20} />, href: '/audit-logs', roles: ['MANAGER', 'ADMIN'] },
    { label: 'Profile', icon: <User size={20} />, href: '/profile' },
];

function filterByRole(items: NavItem[], role: Role | undefined): NavItem[] {
    if (!role) return [];
    return items.filter((item) => !item.roles || item.roles.includes(role));
}

function isRouteActive(currentPath: string, href: string): boolean {
    if (href === '/') return currentPath === '/';
    return currentPath === href || currentPath.startsWith(`${href}/`);
}

function getNavLinkClass(isActive: boolean, isOpen: boolean): string {
    return cn(
        'group flex items-center gap-2 rounded-md py-2 text-sm transition-colors duration-150',
        isOpen ? 'px-4' : 'justify-center px-2',
        isActive
            ? 'bg-subtle text-text-primary font-semibold'
            : 'text-text-secondary hover:bg-subtle/70 hover:text-text-primary',
    );
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
            {isOpen && (
                <button
                    type="button"
                    aria-label="Close sidebar"
                    className="fixed inset-0 z-40 bg-black/20 md:hidden"
                    onClick={onToggle}
                />
            )}

            <aside
                className={cn(
                    'flex flex-col bg-primary p-4',
                    'border-r border-border-default',
                    'transition-all duration-300',
                    'z-50 shrink-0 overflow-hidden',
                    'fixed inset-y-0 left-0 md:relative',
                    isOpen ? 'w-sidebar translate-x-0' : 'w-sidebar-collapsed -translate-x-full md:translate-x-0',
                )}
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
                            const isActive = isRouteActive(currentPath, item.href);
                            return (
                                <li key={item.href}>
                                    <Link
                                        to={item.href}
                                        title={!isOpen ? item.label : undefined}
                                        aria-current={isActive ? 'page' : undefined}
                                        className={getNavLinkClass(isActive, isOpen)}
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
                                    const isActive = isRouteActive(currentPath, item.href);
                                    return (
                                        <li key={item.href}>
                                            <Link
                                                to={item.href}
                                                title={!isOpen ? item.label : undefined}
                                                aria-current={isActive ? 'page' : undefined}
                                                className={getNavLinkClass(isActive, isOpen)}
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
                            const isActive = isRouteActive(currentPath, item.href);
                            return (
                                <li key={item.href}>
                                    <Link
                                        to={item.href}
                                        title={!isOpen ? item.label : undefined}
                                        aria-current={isActive ? 'page' : undefined}
                                        className={getNavLinkClass(isActive, isOpen)}
                                    >
                                        <span className="shrink-0">{item.icon}</span>
                                        {isOpen && <span className="truncate">{item.label}</span>}
                                    </Link>
                                </li>
                            );
                        })}
                    </ul>
                </nav>
            </aside>
        </>
    );
}
