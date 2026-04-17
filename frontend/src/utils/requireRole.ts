import { redirect } from '@tanstack/react-router';
import type { Role } from '~/types/api';

/**
 * Route guard: throws a redirect to /login (or a fallback) if the user's role
 * is not in the allowed list.
 */
export function requireRole(allowedRoles: Role[], userRole: Role | undefined, redirectTo = '/login') {
    if (!userRole || !allowedRoles.includes(userRole)) {
        throw redirect({ to: redirectTo });
    }
}
