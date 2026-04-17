import { useState } from 'react';
import type { PropsWithChildren } from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { cn } from '~/utils/cn';

export function DefaultLayout({ children }: PropsWithChildren) {
    const [sidebarOpen, setSidebarOpen] = useState(true);

    return (
        <div className="flex h-screen w-screen overflow-hidden bg-[#f5f5f0]">
            {/* Sidebar */}
            <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />

            {/* Main area */}
            <div className="flex flex-1 flex-col overflow-hidden">
                {/* Header */}
                <Header
                    isSidebarOpen={sidebarOpen}
                    onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
                />

                {/* Content Container */}
                <main
                    className={cn(
                        'flex-1 overflow-y-auto overflow-x-hidden',
                        'transition-all duration-300',
                    )}
                    style={{ padding: '3rem' }}
                >
                    <div className="mx-auto max-w-5xl w-full">
                        {children}
                    </div>
                </main>
            </div>
        </div>
    );
}
