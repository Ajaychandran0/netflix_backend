import { Request, Response, NextFunction } from 'express';
import { validationResult } from 'express-validator';
import { apiError } from '../utils/apiResponse';
import { ErrorCodes } from '../constants/ResponseCodes';

export const handleValidationErrors = (req: Request, res: Response, next: NextFunction) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
     apiError({
      res,
      message: 'Invalid request',
      statusCode: 422,
      error: errors.array(),
      code: ErrorCodes.DATA_VALIDATION_ERROR,
      enableLogging: true,
      isValidationError: true
    });
    return
  }
  next();
};
