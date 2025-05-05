import { Request, Response, NextFunction } from 'express';
import { serviceMap, Services } from './http/axios.services';
import { apiResponse } from '@/core/utils/apiResponse';
import { asyncErrorHandler } from '@/core/utils/asyncErrorHandler';
import { handleAxiosError } from '@/core/utils/handleAxiosError';

class BaseService {
    httpMethods = ['get', 'post', 'put', 'delete'] as const;

    forward = (
        serviceName: Services,
        method: typeof this.httpMethods[number],
        path: string
    ) => {
        return asyncErrorHandler(async (req: Request, res: Response, next: NextFunction) => {
            const client = serviceMap[serviceName];

            // Extract user information from req.user
            const userHeaders = req.user
                ? {
                    'x-user-id': req.user.id,
                    'x-user-email': req.user.email,
                    'x-user-role': req.user.role,
                }
                : {};

            // Merge original headers with user headers
            const headers = {
                ...req.headers,
                ...userHeaders,
            };

            let axiosResponse;

            if (method === 'get' || method === 'delete') {
                axiosResponse = await client[method](path, {
                    params: req.query,
                    headers
                });
            } else {
                axiosResponse = await client[method](path, req.body, {
                    headers
                });
            }

            const { data } = axiosResponse;

            apiResponse({
                res,
                message: data.message,
                data: data.data,
                statusCode: data.statusCode,
                code: data.code,
            });
        });
    };

    // For internal use (orchestration) where you want the raw response instead of sending to res
    forwardRaw = async (
        res: Response,
        serviceName: Services,
        method: typeof this.httpMethods[number],
        path: string,
        options: {
            data?: any,
            query?: any,
            headers?: any,
        } = {}
    ) => {
        try {
            const client = serviceMap[serviceName];

            const config: any = {
                params: options.query,
                headers: options.headers
            };

            const axiosMethod = method === 'get' || method === 'delete'
                ? client[method](path, config)
                : client[method](path, options.data, config);

            const axiosResponse = await axiosMethod;
            const { data } = axiosResponse;


            apiResponse({
                res,
                message: data.message,
                data: data.data,
                statusCode: data.statusCode,
                code: data.code,
            });
        } catch (error) {
            throw handleAxiosError(error);
        }
    };
}

export const baseService = new BaseService();
