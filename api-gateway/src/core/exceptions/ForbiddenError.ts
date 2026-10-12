import { AppError } from './AppError';
import { ErrorCodes } from '../constants/ResponseCodes';

export class ForbiddenError extends AppError {
  constructor(message = 'Forbidden', code = ErrorCodes.FORBIDDEN) {
    super(message, 403, code);
  }
}
