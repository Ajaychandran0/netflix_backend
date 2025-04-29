import express, { Application } from 'express';
import { router } from './routes';
import { AuthMiddleware } from './middlewares/auth.middleware';
import { RedisClient } from './utils/cache';
import { logger } from './config/logger';
import cors from 'cors';
import compression from 'compression';
import helmet from 'helmet';
import { httpLogger } from './config/httpLogger';


export class App {
  public app: Application;

  constructor() {
    this.app = express();
    this.config();
    this.routes();
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

  }

  private routes(): void {
    this.app.use('/', router);
  }

  public listen(port: string | number): void {
    this.app.listen(port, () => {
      logger.info(`API Gateway running on port ${port}`);
    });
  }
}
