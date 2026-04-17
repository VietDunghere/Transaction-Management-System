import {
    LayoutDashboard,
    ArrowLeftRight,
    ShieldAlert,
    BarChart3,
    GitCompare,
    ChevronLeft,
    ChevronRight,
    LogOut,
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

const navItems: NavItem[] = [
    { label: 'Dashboard', icon: <LayoutDashboard size={20} />, href: '/' },
    { label: 'Transactions', icon: <ArrowLeftRight size={20} />, href: '/transactions' },
    { label: 'Cases & Audit', icon: <ShieldAlert size={20} />, href: '/cases' },
    { label: 'Reports & BI', icon: <BarChart3 size={20} />, href: '/reports' },
    { label: 'Reconciliation', icon: <GitCompare size={20} />, href: '/reconciliation' },
    { label: 'UI Demo', icon: <Component size={20} />, href: '/ui-demo' },
];

export function Sidebar({ isOpen, onToggle }: SidebarProps) {
    const routerState = useRouterState();
    const currentPath = routerState.location.pathname;

    return (
        <>
            {/* Mobile overlay */}
            {isOpen && (
                <div
                    className="fixed inset-0 z-40 bg-black/40 md:hidden"
                    onClick={onToggle}
                />
            )}

            <aside
                className={cn(
                    'flex flex-col bg-white brutal-border',
                    'border-t-0 border-l-0 border-b-0',
                    'transition-all duration-300',
                    'z-50',
                    /* Mobile: overlay drawer */
                    'fixed inset-y-0 left-0 md:relative',
                    isOpen
                        ? 'w-[var(--sidebar-width)] translate-x-0'
                        : 'w-[var(--sidebar-collapsed)] -translate-x-full md:translate-x-0',
                )}
            >
                {/* Logo */}
                <div
                    className={cn(
                        'flex items-center gap-4 border-b-2 border-[#1a1a1a]',
                        'h-[var(--header-height)] px-6 shrink-0',
                    )}
                >
                    <div className="flex size-9 items-center justify-center rounded-sm bg-[#1a1a1a] text-white font-black text-base">
                        HF
                    </div>
                    {isOpen && (
                        <span className="text-base font-bold tracking-tight hover:text-[#1a1a1a]/80 transition-colors">
                            <Link to="/">Huza Fraud</Link>
                        </span>
                    )}
                </div>

                {/* Nav items */}
                <nav className="flex-1 overflow-y-auto py-4">
                    <ul className="flex flex-col gap-2">
                        {navItems.map((item) => {
                            const isActive = currentPath === item.href || currentPath.startsWith(item.href + '/');
                            return (
                                <li key={item.href}>
                                    <Link
                                        to={item.href}
                                        className={cn(
                                            'flex items-center gap-4',
                                            'mx-4 px-4 py-3',
                                            'rounded-lg transition-all duration-150',
                                            'text-base font-medium border-2 border-transparent',
                                            'hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-[2px_2px_0_0_#1a1a1a] hover:border-[#1a1a1a]',
                                            isActive
                                                ? 'bg-[#e5e5e5] text-[#1a1a1a] font-bold border-[#1a1a1a]'
                                                : 'text-[#525252] hover:bg-[#f5f5f0] hover:text-[#1a1a1a]',
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

                {/* Footer */}
                <div className="border-t-2 border-[#1a1a1a] p-2">
                    {/* Toggle button */}
                    <button
                        onClick={onToggle}
                        className={cn(
                            'hidden md:flex w-full items-center gap-4',
                            'mx-4 px-4 py-2 w-auto',
                            'rounded-sm text-[#525252]',
                            'hover:bg-[#f5f5f0] hover:text-[#1a1a1a]',
                            'transition-colors duration-150',
                            'text-sm',
                        )}
                    >
                        <span className="shrink-0">
                            {isOpen ? <ChevronLeft size={18} /> : <ChevronRight size={18} />}
                        </span>
                        {isOpen && <span>Collapse</span>}
                    </button>

                    {/* Logout placeholder */}
                    <button
                        className={cn(
                            'flex w-full items-center gap-4',
                            'mx-4 px-4 py-2 w-auto',
                            'rounded-sm text-[#ef4444]',
                            'hover:bg-red-50',
                            'transition-colors duration-150',
                            'text-sm',
                        )}
                    >
                        <span className="shrink-0"><LogOut size={18} /></span>
                        {isOpen && <span>Log out</span>}
                    </button>
                </div>
            </aside>
        </>
    );
}
