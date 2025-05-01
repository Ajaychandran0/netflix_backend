import jwt from 'jsonwebtoken';
import { env } from '../config/env';


interface Payload {
    userId: string;
    email: string;
    role: number;
}

export const verifyToken = (token: string): Payload => {
    try {
        return jwt.verify(token, env.JWT_SECRET) as Payload;
    } catch (error) {
        throw new Error('Invalid or expired token');
    }
};
