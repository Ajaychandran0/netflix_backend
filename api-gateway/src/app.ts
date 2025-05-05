import express, { Application, NextFunction, Request, Response } from 'express';
import 'express-async-errors';
import { urlencoded } from 'body-parser';
import compression from 'compression';
import helmet from 'helmet';
import cors from 'cors';

// Import custom modules
import { RedisClient } from './core/utils/cache';
import { logger } from './core/config/logger';
import { httpLogger } from './core/config/httpLogger';
import { errorHandler } from './core/middlewares/errorHandler';
import appRoutes from './routes';

export class App {
  public app: Application;

  constructor() {
    this.app = express();
    this.config();
    this.routes();
    this.handleErrors();
  }

  private config(): void {
    this.app.use(compression()); // Enable compression
    this.app.use(helmet()); // Set security headers
    this.app.use(httpLogger); // HTTP request logging
    this.app.use(express.json());

    // Init Redis connection
    RedisClient.init();

    // Enable CORS
    this.app.use(cors({
      origin: '*', // Replace with a more secure list of allowed origins
      methods: 'GET,HEAD,PUT,PATCH,POST,DELETE',
      allowedHeaders: 'Content-Type, Authorization',
    }));

    // Parse URL-encoded bodies (for form submissions)
    this.app.use(urlencoded({ extended: true }));

  }

  private routes(): void {
    this.app.use('/api', appRoutes);

    this.app.get("/", (req: Request, res: Response) => {
      res.send({ code: "SUCCESS", message: 'API Gateway running' });
    })
  }

  private handleErrors(): void {
    this.app.use((err: unknown, req: Request, res: Response, next: NextFunction) => {
      errorHandler(err, req, res, next);
    });
  }

  public listen(port: string | number): void {
    this.app.listen(port, () => {
      logger.info(`API Gateway running on port ${port}`);
    });
  }
}
