import { AppError } from './AppError';
import { ErrorCodes } from '../constants/ResponseCodes';

export class NotFoundError extends AppError {
    constructor(message = 'Not Found', code = ErrorCodes.NOT_FOUND) {
        super(message, 404, code);
    }
}
