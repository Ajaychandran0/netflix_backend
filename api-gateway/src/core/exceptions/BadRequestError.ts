import { AppError } from './AppError';
import { ErrorCodes } from '../constants/ResponseCodes';

export class BadRequestError extends AppError {
  constructor(message = 'Bad Request', code = ErrorCodes.BAD_REQUEST) {
    super(message, 400, code);
  }
}
