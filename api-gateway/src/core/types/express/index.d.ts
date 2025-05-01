import { JwtPayload } from 'jsonwebtoken';

declare module 'express-serve-static-core' {
  interface Request {
    user?: string | JwtPayload;
    userDetails?: Record<string, any>; // You can define a User type if you prefer
  }
}
