import { useState } from 'react';
import type { PropsWithChildren } from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { RightBar } from './RightBar';
import { cn } from '~/utils/cn';

export function DefaultLayout({ children }: PropsWithChildren) {
    const [sidebarOpen, setSidebarOpen] = useState(true);

    return (
        <div className="flex h-screen w-screen overflow-hidden bg-[var(--color-bg-primary)]">
            {/* Sidebar */}
            <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />

            {/* Main column (Header + Content) */}
            <div className="flex flex-1 flex-col overflow-hidden min-w-0">
                <Header isSidebarOpen={sidebarOpen} onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />

                <main
                    className={cn('flex-1 overflow-y-auto overflow-x-hidden', 'bg-[var(--color-bg-primary)]')}
                    style={{ padding: 28 }}
                >
                    {children}
                </main>
            </div>

            {/* Right Bar */}
            <RightBar />
        </div>
    );
}
