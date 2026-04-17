import { useNavigate } from '@tanstack/react-router';
import { FileQuestion } from 'lucide-react';
import { Button } from '~/components/ui/Button/Button';

export function NotFoundPage() {
    const navigate = useNavigate();

    return (
        <div className="flex flex-col items-center justify-center h-[60vh] gap-4">
            <FileQuestion size={48} className="text-[var(--color-text-tertiary)]" />
            <p className="text-4xl font-bold text-[var(--color-text-primary)]">404</p>
            <p className="text-sm text-[var(--color-text-secondary)]">The page you're looking for doesn't exist.</p>
            <Button variant="secondary" onClick={() => navigate({ to: '/' })}>
                Go to Dashboard
            </Button>
        </div>
    );
}
