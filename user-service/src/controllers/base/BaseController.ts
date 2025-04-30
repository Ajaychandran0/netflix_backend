import { Request, Response, NextFunction } from 'express';
import { logger } from "@core/config/logger"

// Abstract class to handle basic request logic
export abstract class BaseController {
  // Abstract method for route handling, to be implemented by subclasses
  abstract handleRequest(req: Request, res: Response, next: NextFunction): Promise<void>;

  // This method wraps the actual route logic and catches errors
  public execute(req: Request, res: Response, next: NextFunction) {
    this.handleRequest(req, res, next).catch((error) => {
      logger.error('Error in BaseController:', error);
      next(error);
    });
  }
}
