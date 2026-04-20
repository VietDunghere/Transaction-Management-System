import { Outlet } from '@tanstack/react-router';

export function PublicLayout() {
    return (
        <div className="flex min-h-screen items-center justify-center bg-secondary p-4 sm:p-8 font-sans transition-colors duration-700 ease-in-out">
            <Outlet />
        </div>
    );
}
