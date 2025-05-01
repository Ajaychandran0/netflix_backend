import axios, { AxiosInstance } from 'axios';
import { SERVICE_URLS } from './axios.config';
import { env } from '@/core/config/env';

const createAxiosInstance = (baseURL: string): AxiosInstance => {
    const instance = axios.create({
        baseURL,
        timeout: 5000,
        headers: {
            'Content-Type': 'application/json',
        },
    });

    // Add request interceptor
    instance.interceptors.request.use((config) => {
        config.headers['x-internal-api-key'] = env.INTERNAL_API_KEY || '';
        return config;
    });

    // Add response interceptor
    instance.interceptors.response.use(
        (response) => response,
        (error) => {
            return Promise.reject(error);
        }
    );

    return instance;
};

export const userServiceAxios = createAxiosInstance(SERVICE_URLS.USER_SERVICE);
// export const contentServiceAxios = createAxiosInstance(SERVICE_URLS.CONTENT_SERVICE);