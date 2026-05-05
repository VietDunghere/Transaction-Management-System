export function ensureCryptoRandomUUID(): void {
    const fallback = (): string => `uuid-${Date.now()}-${Math.random().toString(16).slice(2, 10)}`;

    const globalObj = globalThis as typeof globalThis & {
        crypto?: Crypto & { randomUUID?: () => string };
    };

    if (!globalObj.crypto) {
        Object.defineProperty(globalObj, 'crypto', {
            value: { randomUUID: fallback },
            configurable: true,
        });
        return;
    }

    if (typeof globalObj.crypto.randomUUID !== 'function') {
        Object.defineProperty(globalObj.crypto, 'randomUUID', {
            value: fallback,
            configurable: true,
        });
    }
}
