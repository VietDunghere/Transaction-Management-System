const _uuidFallback = (): string =>
    'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
        const r = (Math.random() * 16) | 0;
        return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16);
    });

export function ensureCryptoRandomUUID(): void {
    if (typeof globalThis.crypto?.randomUUID === 'function') return;

    // Attempt 1: patch the existing crypto object directly.
    try {
        Object.defineProperty(globalThis.crypto, 'randomUUID', {
            value: _uuidFallback,
            configurable: true,
            writable: true,
            enumerable: true,
        });
        if (typeof globalThis.crypto.randomUUID === 'function') return;
    } catch { /* native Crypto is sealed — fall through */ }

    // Attempt 2: replace globalThis.crypto with a plain wrapper that adds randomUUID.
    try {
        const orig = globalThis.crypto as Crypto;
        const patched = Object.create(Object.getPrototypeOf(orig)) as Crypto & { randomUUID: () => string };
        Object.defineProperties(patched, {
            ...Object.getOwnPropertyDescriptors(orig),
            randomUUID: { value: _uuidFallback, configurable: true, writable: true, enumerable: true },
        });
        Object.defineProperty(globalThis, 'crypto', {
            value: patched,
            configurable: true,
            writable: true,
        });
        if (typeof globalThis.crypto.randomUUID === 'function') return;
    } catch { /* fall through */ }

    // Attempt 3: brute-force assign.
    (globalThis as Record<string, unknown>)['crypto'] = { randomUUID: _uuidFallback };
}
