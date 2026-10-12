import jwt, { SignOptions } from 'jsonwebtoken';
import { env } from '../config/env';
import { AuthenticatedUser } from '../types/user';

export const generateToken = (
  payload: AuthenticatedUser,
  options: SignOptions = { expiresIn: '1h' }
): string => {
  return jwt.sign(payload, env.JWT_SECRET, options);
};