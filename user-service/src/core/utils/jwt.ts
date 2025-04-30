import jwt, { SignOptions } from 'jsonwebtoken';
import { env } from '../config/env';

interface Payload {
  userId: string;
  email: string;
  role: number;
}

export const generateToken = (
  payload: Payload,
  options: SignOptions = { expiresIn: '1h' }
): string => {
  return jwt.sign(payload, env.JWT_SECRET, options);
};