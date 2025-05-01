import { AppError } from './AppError';
import { ErrorCodes } from '../constants/ResponseCodes';

export class InternalServerError extends AppError {
  constructor(message = 'Internal Server Error', code = ErrorCodes.INTERNAL_SERVER_ERROR) {
    super(message, 500, code);
  }
}
