import { AxiosInstance } from 'axios';
import { userServiceAxios } from './axios.instance';

export type Services = "user-service" | "content-service" 

export const serviceMap: Record<Services, AxiosInstance> = {
    "user-service": userServiceAxios,
    "content-service": userServiceAxios, 
}


