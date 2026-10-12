import axios, { AxiosError } from 'axios';
import { AppError } from '../exceptions/AppError';
import { ErrorCodes } from '../constants/ResponseCodes';
import { ResponseMessages } from '../constants/ResponseMessages';

export function handleAxiosError(error: unknown): never {
    if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError<any>;

        // Check if the response contains a structured error from a service
        if (axiosError.response && axiosError.response.data) {
            const data = axiosError.response.data;

            const message = data.message || ResponseMessages.SERVICE_ERROR;
            const statusCode = axiosError.response.status || 500;
            const code = data.code || ErrorCodes.SERVICE_ERROR;

            throw new AppError(message, statusCode, code, axiosError);
        }

        // Network or unknown Axios error
        throw new AppError(
            axiosError.message || ResponseMessages.SERVICE_UNAVAILABLE,
            503,
            ErrorCodes.SERVICE_UNAVAILABLE,
            axiosError,
        );
    }

    // If not an Axios error, throw as internal error
    throw new AppError(ResponseMessages.INTERNAL_SERVER_ERROR, 500, ErrorCodes.INTERNAL_SERVER_ERROR, error);
}