import { Request, Response, NextFunction } from 'express';
import { verifyToken } from '../utils/jwt';
import { UnauthorizedError } from '../exceptions/UnauthorizedError';
import { ErrorCodes } from '../constants/ResponseCodes';


export function authenticate(req: Request, res: Response, next: NextFunction) {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    throw new UnauthorizedError()
  }

  try {
    const token = authHeader.split(' ')[1];
    const payload = verifyToken(token);

    req.user = {
      id: payload.id,
      email: payload.email,
      role: payload.role
    };

    next();
  } catch (error) {
    throw new UnauthorizedError('Invalid or expired token', ErrorCodes.INVALID_TOKEN);
  }
}
