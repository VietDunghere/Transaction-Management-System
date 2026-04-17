import { createAxiosInstance } from '~/api/callApi';

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1';

export const apiClient = createAxiosInstance(BASE_URL);
