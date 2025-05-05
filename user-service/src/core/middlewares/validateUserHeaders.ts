// validateUserHeaders.ts
import { NextFunction, Request, Response } from 'express';
import { header, validationResult } from 'express-validator';
import { apiError } from '../utils/apiResponse';
import { ErrorCodes } from '../constants/ResponseCodes';

export const validateUserHeaders = [
    header('x-user-id').exists().withMessage("Missing x-user-id").bail().isUUID().withMessage('Invalid x-user-id'),
    header('x-user-email').exists().withMessage('Missing x-user-email').bail().isEmail().withMessage('Invalid x-user-email'),
    header('x-user-role').exists().withMessage("Missing x-user-role").bail().isString().withMessage('Invalid x-user-role'),
    (req: Request, res: Response, next: NextFunction) => {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
            apiError({
                res,
                message: 'Invalid request header',
                statusCode: 400,
                error: errors.array(),
                code: ErrorCodes.HEADER_VALIDATION_ERROR,
                enableLogging: true,
                isValidationError: true
            });
            return
        }
        next();
    }
];
