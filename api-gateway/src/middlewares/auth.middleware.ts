import { Request, Response, NextFunction } from 'express';

export function AuthMiddleware(req: Request, res: Response, next: NextFunction) {
  const authHeader = req.headers.authorization;

  if (!authHeader) {
    return res.status(401).json({ message: 'Missing auth header' });
  }

  // Here you would validate the JWT token or API key
  // For now just log and continue
  console.log('Auth Middleware passed');
  next();
}
