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
  const response = {
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
}: ErrorResponseOptions) => {
  const response = {
    success: false,
    message,
    code,
    localeMessageKey,
  };

  if (enableLogging) {
    logger.error(`[${statusCode}] ${message} ${code ? `| Code: ${code}` : ''}`, error);
  }

  return res.status(statusCode).json(response);
};