// utils/errors/UnauthorizedError.ts
import { AppError } from './AppError'
import { ErrorCodes } from '../constants/ResponseCodes';

export class UnauthorizedError extends AppError {
  constructor(message = 'Unauthorized', code = ErrorCodes.UNAUTHORIZED) {
    super(message, 401, code);
  }
}