import { toast } from 'sonner';

const IGNORED_CLIENT_ERROR_PATTERNS: RegExp[] = [
    /crypto\.randomUUID is not a function/i,
];

function extractMessage(error: unknown): string | undefined {
    const apiMsg = (error as any)?.response?.data?.message;
    if (typeof apiMsg === 'string' && apiMsg.trim().length > 0) {
        return apiMsg.trim();
    }

    if (error instanceof Error && error.message.trim().length > 0) {
        return error.message.trim();
    }

    return undefined;
}

function shouldIgnoreMessage(message: string): boolean {
    return IGNORED_CLIENT_ERROR_PATTERNS.some((pattern) => pattern.test(message));
}

export function toastMutationError(error: unknown, fallbackMessage = 'Something went wrong'): void {
    const message = extractMessage(error) ?? fallbackMessage;
    if (shouldIgnoreMessage(message)) {
        return;
    }
    toast.error(message);
}
