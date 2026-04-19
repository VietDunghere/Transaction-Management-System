import { create } from 'zustand';

type Theme = 'light' | 'dark';

function getStoredTheme(): Theme {
    try {
        const stored = localStorage.getItem('theme');
        if (stored === 'light' || stored === 'dark') return stored;
    } catch {}
    return 'light';
}

function applyTheme(theme: Theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
}

interface UIState {
    sidebarCollapsed: boolean;
    theme: Theme;
    toggleSidebar: () => void;
    setSidebarCollapsed: (collapsed: boolean) => void;
    toggleTheme: () => void;
}

// Apply stored theme on load
const initialTheme = getStoredTheme();
applyTheme(initialTheme);

export const useUIStore = create<UIState>((set) => ({
    sidebarCollapsed: false,
    theme: initialTheme,
    toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
    setSidebarCollapsed: (sidebarCollapsed) => set({ sidebarCollapsed }),
    toggleTheme: () =>
        set((s) => {
            const next = s.theme === 'light' ? 'dark' : 'light';
            applyTheme(next);
            return { theme: next };
        }),
}));
