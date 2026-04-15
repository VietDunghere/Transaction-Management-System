import { useState, useEffect } from 'react';

/**
 * Hook tùy chỉnh để theo dõi trạng thái của một truy vấn phương tiện (media query).
 *
 * @param query - Chuỗi truy vấn phương tiện CSS (ví dụ: '(min-width: 768px)')
 * @returns Trả về true nếu truy vấn khớp, ngược lại là false.
 */
export function useMediaQuery(query: string): boolean {
    const getInitialState = (query: string): boolean => {
        if (typeof window === 'undefined') {
            return false;
        }
        try {
            return window.matchMedia(query).matches;
        } catch (e) {
            console.error('Lỗi khi sử dụng matchMedia:', e);
            return false;
        }
    };
    const [matches, setMatches] = useState<boolean>(() => getInitialState(query));

    useEffect(() => {
        if (typeof window === 'undefined') {
            return;
        }
        const mediaQueryList: MediaQueryList = window.matchMedia(query);
        const listener = (event: MediaQueryListEvent) => {
            setMatches(event.matches);
        };
        mediaQueryList.addEventListener('change', listener);
        return () => {
            mediaQueryList.removeEventListener('change', listener);
        };
    }, [query]); 

    return matches;
}
export default useMediaQuery; 
