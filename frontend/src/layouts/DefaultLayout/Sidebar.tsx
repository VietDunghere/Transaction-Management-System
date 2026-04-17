import {
    LayoutDashboard,
    ArrowLeftRight,
    ShieldAlert,
    BarChart3,
    GitCompare,
    User,
    FileText,
    Target,
    Zap,
    CheckSquare,
    ChevronRight,
    Component,
} from 'lucide-react';
import { Link, useRouterState } from '@tanstack/react-router';
import { cn } from '~/utils/cn';

interface SidebarProps {
    isOpen: boolean;
    onToggle: () => void;
}

interface NavItem {
    label: string;
    icon: React.ReactNode;
    href: string;
}

const dashboardItems: NavItem[] = [
    { label: 'Default', icon: <LayoutDashboard size={20} />, href: '/' },
    { label: 'Transactions', icon: <ArrowLeftRight size={20} />, href: '/transactions' },
    { label: 'Cases & Audit', icon: <ShieldAlert size={20} />, href: '/cases' },
];

const pageItems: NavItem[] = [
    { label: 'User Profile', icon: <User size={20} />, href: '/profile' },
    { label: 'Reports & BI', icon: <BarChart3 size={20} />, href: '/reports' },
    { label: 'Reconciliation', icon: <GitCompare size={20} />, href: '/reconciliation' },
    { label: 'Campaigns', icon: <Target size={20} />, href: '/campaigns' },
    { label: 'Documents', icon: <FileText size={20} />, href: '/documents' },
    { label: 'Resources', icon: <Zap size={20} />, href: '/resources' },
    { label: 'Tasks', icon: <CheckSquare size={20} />, href: '/tasks' },
    { label: 'UI Demo', icon: <Component size={20} />, href: '/ui-demo' },
];

const topNavItems = [
    { label: 'Overview', href: '/' },
    { label: 'Projects', href: '/projects' },
];

export function Sidebar({ isOpen, onToggle }: SidebarProps) {
    const routerState = useRouterState();
    const currentPath = routerState.location.pathname;

    return (
        <>
            {/* Mobile overlay */}
            {isOpen && <div className="fixed inset-0 z-40 bg-black/20 md:hidden" onClick={onToggle} />}

            <aside
                className={cn(
                    'flex flex-col bg-[var(--color-bg-primary)]',
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
                    <div className="flex size-6 shrink-0 items-center justify-center rounded-full bg-[var(--color-bg-accent-purple)]">
                        <span className="text-[10px] font-semibold text-[var(--color-text-on-accent)]">B</span>
                    </div>
                    {isOpen && <span className="text-sm font-normal text-[var(--color-text-primary)]">ByeWind</span>}
                </div>

                {/* Top nav (Overview, Projects) */}
                <nav className="flex flex-col gap-1 mb-2">
                    {topNavItems.map((item) => {
                        const isActive = currentPath === item.href;
                        return (
                            <Link
                                key={item.href}
                                to={item.href}
                                className={cn(
                                    'flex items-center gap-2 px-2 py-2 rounded-sm',
                                    'text-sm transition-colors duration-150',
                                    isActive
                                        ? 'text-[var(--color-text-primary)] font-semibold'
                                        : 'text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]',
                                )}
                            >
                                <span className="size-1.5 rounded-full bg-current shrink-0" />
                                {isOpen && <span>{item.label}</span>}
                            </Link>
                        );
                    })}
                </nav>

                {/* Scrollable nav area */}
                <nav className="flex-1 overflow-y-auto">
                    {/* DASHBOARDS section */}
                    {isOpen && (
                        <div className="px-3 py-1 mb-1">
                            <span className="text-xs font-normal text-[var(--color-text-secondary)] uppercase tracking-wider">
                                Dashboards
                            </span>
                        </div>
                    )}
                    <ul className="flex flex-col gap-0.5">
                        {dashboardItems.map((item) => {
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

                    {/* PAGES section */}
                    {isOpen && (
                        <div className="px-3 py-1 mt-4 mb-1">
                            <span className="text-xs font-normal text-[var(--color-text-secondary)] uppercase tracking-wider">
                                Pages
                            </span>
                        </div>
                    )}
                    <ul className="flex flex-col gap-0.5">
                        {pageItems.map((item) => {
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

                {/* Footer — SnowUI logo */}
                {isOpen && (
                    <div className="flex items-center gap-2 px-2 py-2 mt-2">
                        <div className="flex size-5 items-center justify-center rounded-sm bg-[var(--color-accent-indigo)]">
                            <span className="text-[8px] font-semibold text-white">S</span>
                        </div>
                        <span className="text-xs text-[var(--color-text-secondary)]">SnowUI</span>
                    </div>
                )}
            </aside>
        </>
    );
}
