import { Response } from 'express';
import { logger } from '../config/logger';

interface SuccessResponseOptions {
  res: Response;
  message: string;
  data?: unknown;
  statusCode?: number;
  code?: string;
  localeMessageKey?: string;
  enableLogging?: boolean;
}

interface ErrorResponseOptions {
  res: Response;
  message: string;
  statusCode?: number;
  error?: unknown;
  code?: string;
  localeMessageKey?: string;
  enableLogging?: boolean;
  isValidationError?: boolean;
}

interface APIResponse {
  success: boolean;
  message: string;
  code?: string;
  localeMessageKey?: string;
  data?: unknown;
  errors?: unknown;
}

export const apiResponse = ({
  res,
  message,
  data = {},
  statusCode = 200,
  code,
  localeMessageKey,
  enableLogging = false,
}: SuccessResponseOptions) => {
  const response: APIResponse = {
    success: true,
    message,
    code,
    localeMessageKey,
    data,
  };

  if (enableLogging) {
    logger.info(`[${statusCode}] ${message} ${code ? `| Code: ${code}` : ''}`);
  }

  return res.status(statusCode).json(response);
};

export const apiError = ({
  res,
  message,
  statusCode = 500,
  error,
  code,
  localeMessageKey,
  enableLogging = true,
  isValidationError = false,
}: ErrorResponseOptions) => {
  const response: APIResponse = {
    success: false,
    message,
    code,
    localeMessageKey,
  };

  if (isValidationError) {
    response.errors = error;
  }

  if (enableLogging) {
    logger.error(`[${statusCode}] ${message} ${code ? `| Code: ${code}` : ''}`);
    logger.error(error)
  }

  return res.status(statusCode).json(response);
};