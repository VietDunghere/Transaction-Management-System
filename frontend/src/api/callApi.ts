import axios, { type AxiosInstance } from 'axios';
import { getAccessToken, removeAccessToken } from '~/utils/localStorage.ts';

export function createAxiosInstance(baseURL: string): AxiosInstance {
    const instance = axios.create({
        baseURL,
        headers: {
            'Content-Type': 'application/json',
        },
    });

    instance.interceptors.request.use(
        (config) => {
            const token = getAccessToken();
            if (token && config.headers) {
                config.headers.Authorization = `Bearer ${token}`;
            }
            return config;
        },
        (error) => {
            return Promise.reject(error);
        }
    );

    instance.interceptors.response.use(
        (response) => {
            return response.data;
        },
        (error) => {
            const status = error.response?.status;

            if (status === 401) {
                removeAccessToken();
                return Promise.reject(error);
            } else if (status === 403 || status === 404) {
                console.error(`Error ${status}: `, error.response?.data?.message);
            }
            if (status === 422) {
                return Promise.resolve(error.response.data);
            }
            return Promise.reject(error);
        }
    );

    return instance;
}