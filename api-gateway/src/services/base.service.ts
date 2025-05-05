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
            console.log(req.user, "user is ddddd i n api-gateway");
            const client = serviceMap[serviceName];

            let axiosResponse;

            if (method === 'get' || method === 'delete') {
                axiosResponse = await client[method](path, {
                    params: req.query,
                });
            } else {
                axiosResponse = await client[method](path, req.body);
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
        } = {}
    ) => {
        try {
            const client = serviceMap[serviceName];

            const config: any = {
                params: options.query,
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
