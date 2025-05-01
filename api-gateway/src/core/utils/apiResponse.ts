import { Response } from 'express';
import { logger } from '../config/logger';
import { env } from '../config/env';

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
    const isExpectedError = statusCode < 500; // Anything < 500 is client-related
    const logLevel = isExpectedError ? 'info' : 'error';

    const logPayload: Record<string, unknown> = {
      statusCode,
      message,
      code,
    };

    if (env.NODE_ENV !== 'production' || !isExpectedError) {
      logPayload.stack = (error as any)?.stack;
      logPayload.cause = (error as any)?.cause;
    }

    logger[logLevel](`[${statusCode}] ${message} ${code ? `| Code: ${code}` : ''}`, logPayload);
  }

  return res.status(statusCode).json(response);
};