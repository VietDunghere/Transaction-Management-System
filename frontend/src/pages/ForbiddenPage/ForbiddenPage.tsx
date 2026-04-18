import { useNavigate } from '@tanstack/react-router';
import { ShieldX } from 'lucide-react';
import { Button } from '~/components/ui/Button/Button';

export function ForbiddenPage() {
    const navigate = useNavigate();

    return (
        <div className="flex flex-col items-center justify-center h-[60vh] gap-4">
            <ShieldX size={48} className="text-status-danger" />
            <p className="text-4xl font-bold text-text-primary">403</p>
            <p className="text-sm text-text-secondary">You don't have permission to access this page.</p>
            <Button variant="secondary" onClick={() => navigate({ to: '/' })}>
                Go to Dashboard
            </Button>
        </div>
    );
}
