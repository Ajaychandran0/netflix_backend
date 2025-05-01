import { Request, Response, NextFunction } from 'express';
import { userServiceAxios } from './http/axios.instance';
import { asyncErrorHandler } from '@/core/utils/asyncErrorHandler';
import { apiResponse } from '@/core/utils/apiResponse';

export const signup = asyncErrorHandler(async (req: Request, res: Response, next: NextFunction) => {
  const response = await userServiceAxios.post('/api/auth/register', req.body);

  apiResponse({
    res,
    message: response.data.message,
    data: response.data.data,
    statusCode: response.data.statusCode,
    code: response.data.code,
  });
})

export const signin = asyncErrorHandler(async (req: Request, res: Response, next: NextFunction) => {
  const response = await userServiceAxios.post('/api/auth/signin', req.body);
  apiResponse({
    res,
    message: response.data.message,
    data: response.data.data,
    statusCode: response.data.statusCode,
    code: response.data.code,
  })
  res.status(response.status).json(response.data);
})

export const getProfile = asyncErrorHandler(async (req: Request, res: Response, next: NextFunction) => {
  const token = req.headers.authorization;
  const response = await userServiceAxios.get('/api/user/profile', {
    headers: { Authorization: token },
  });
  apiResponse({
    res, 
    message: response.data.message,
    data: response.data.data,
    statusCode: response.data.statusCode,
    code: response.data.code,
  });
})

export const updateProfile = asyncErrorHandler(async (req: Request, res: Response, next: NextFunction) => {
  const token = req.headers.authorization;
  const response = await userServiceAxios.put('/api/user/update', req.body, {
    headers: { Authorization: token },
  });

  apiResponse({
    res,
    message: response.data.message,
    data: response.data.data,
    statusCode: response.data.statusCode,
    code: response.data.code,
  })
  res.status(response.status).json(response.data);
})

