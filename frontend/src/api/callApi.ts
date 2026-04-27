import axios, { type AxiosInstance, type InternalAxiosRequestConfig } from 'axios';
import { getAccessToken, getRefreshToken, setAccessToken, clearTokens } from '~/utils/localStorage';

let isRefreshing = false;
let isLoggingOut = false;
let failedQueue: { resolve: (token: string) => void; reject: (err: unknown) => void }[] = [];

export function setLoggingOut(value: boolean) {
    isLoggingOut = value;
}

function processQueue(error: unknown, token: string | null) {
    failedQueue.forEach((prom) => {
        if (token) prom.resolve(token);
        else prom.reject(error);
    });
    failedQueue = [];
}

export function createAxiosInstance(baseURL: string): AxiosInstance {
    const instance = axios.create({
        baseURL,
        headers: {
            'Content-Type': 'application/json',
        },
    });

    // ---- Request: attach Bearer token ----
    instance.interceptors.request.use(
        (config) => {
            const token = getAccessToken();
            if (token && config.headers) {
                config.headers.Authorization = `Bearer ${token}`;
            }
            return config;
        },
        (error) => Promise.reject(error),
    );

    // ---- Response: unwrap data + refresh on 401 ----
    instance.interceptors.response.use(
        (response) => response.data,
        async (error) => {
            const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
            const status = error.response?.status;

            // 401 → attempt token refresh (once), but skip for auth endpoints
            const isAuthRequest =
                originalRequest.url?.includes('/auth/login') || originalRequest.url?.includes('/auth/refresh');
            if (status === 401 && !originalRequest._retry && !isAuthRequest) {
                const refreshToken = getRefreshToken();

                if (!refreshToken) {
                    if (!isLoggingOut) {
                        clearTokens();
                        window.location.href = '/login';
                    }
                    return Promise.reject(error);
                }

                if (isRefreshing) {
                    // Queue this request until the refresh completes
                    return new Promise<string>((resolve, reject) => {
                        failedQueue.push({ resolve, reject });
                    }).then((token) => {
                        originalRequest.headers.Authorization = `Bearer ${token}`;
                        return instance(originalRequest);
                    });
                }

                originalRequest._retry = true;
                isRefreshing = true;

                try {
                    const { data } = await axios.post(`${baseURL}/auth/refresh`, {
                        refresh_token: refreshToken,
                    });
                    const newToken: string = data.access_token;
                    setAccessToken(newToken);
                    processQueue(null, newToken);
                    originalRequest.headers.Authorization = `Bearer ${newToken}`;
                    return instance(originalRequest);
                } catch (refreshError) {
                    processQueue(refreshError, null);
                    if (!isLoggingOut) {
                        clearTokens();
                        window.location.href = '/login';
                    }
                    return Promise.reject(refreshError);
                } finally {
                    isRefreshing = false;
                }
            }

            if (status === 403 || status === 404) {
                console.error(`Error ${status}: `, error.response?.data?.message);
            }

            if (status === 422) {
                return Promise.resolve(error.response.data);
            }

            return Promise.reject(error);
        },
    );

    return instance;
}
