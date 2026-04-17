import clsx, { type ClassValue } from 'clsx';

/** Merge Tailwind classes with conditional support via clsx */
export function cn(...inputs: ClassValue[]) {
    return clsx(inputs);
}
