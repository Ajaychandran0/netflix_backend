import { handleAxiosError } from './handleAxiosError';

export const asyncErrorHandler = <T extends (...args: any[]) => Promise<any>>(fn: T): T => {
  return (async (...args: any[]) => {
    try {
      return await fn(...args);
    } catch (err) {
      handleAxiosError(err); // Transforms into AppError
    }
  }) as T;
};
