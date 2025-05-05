import { Request, Response, NextFunction } from 'express';
import { UnauthorizedError } from '../errors/UnauthorizedError';

export function requireUser(req: Request, res: Response, next: NextFunction) {
  console.log('User ID:', req.user, "user id sssss"); // Log the user ID for debugging
  if (!req.user || !req.user.id) {
    throw new UnauthorizedError()
  }

  next();
}
export function requireAdmin(req: Request, res: Response, next: NextFunction) {
  if (!req.user || req.user.role !== 'admin') {
    throw new UnauthorizedError('Admin access required');
  }

  next();
}