import { Request, Response, NextFunction } from 'express';
import { AppError } from '../exceptions/AppError';
import { apiError } from '../utils/apiResponse';
import { ErrorCodes } from '../constants/ResponseCodes';

export const errorHandler = (
  err: unknown,
  req: Request,
  res: Response,
  next: NextFunction
) => {
  // Handle known AppError
  if (err instanceof AppError) {
    return apiError({
      res,
      message: err.message,
      statusCode: err.statusCode,
      code: err.code,
      error: err,
      enableLogging: true,
    });
  }

  // Handle unknown/unexpected errors
  return apiError({
    res,
    message: 'Internal Server Error',
    statusCode: 500,
    error: err,
    code: ErrorCodes.INTERNAL_SERVER_ERROR,
    enableLogging: true,
  });
};
