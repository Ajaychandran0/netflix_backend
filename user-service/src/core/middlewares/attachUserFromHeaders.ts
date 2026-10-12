import { Request, Response, NextFunction } from 'express';

export function attachUserFromHeaders(req: Request, res: Response, next: NextFunction) {
  const userId = req.headers['x-user-id'] as string;
  const email = req.headers['x-user-email'] as string;
  const role = req.headers['x-user-role'] as string;

  if (userId) {
    req.user = { id: userId, email, role };
  }

  next();
}
