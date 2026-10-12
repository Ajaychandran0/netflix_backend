import { AxiosInstance } from 'axios';
import { userServiceAxios, contentServiceAxios } from './axios.instance';

export type Services = "user-service" | "content-service"

export const serviceMap: Record<Services, AxiosInstance> = {
    "user-service": userServiceAxios,
    "content-service": contentServiceAxios,
}


