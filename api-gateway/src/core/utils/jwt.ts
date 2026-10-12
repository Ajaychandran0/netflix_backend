import jwt from 'jsonwebtoken';
import { env } from '../config/env';
import { UnauthorizedError } from '../exceptions/UnauthorizedError';
import { AuthenticatedUser } from '../types/user';


export const verifyToken = (token: string): AuthenticatedUser => {
    try {
        return jwt.verify(token, env.JWT_SECRET) as AuthenticatedUser;
    } catch (error) {
        throw new UnauthorizedError('Invalid or expired token');
    }
};
