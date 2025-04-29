import express, { Application } from 'express';
import { urlencoded } from 'body-parser';
import compression from 'compression';
import helmet from 'helmet';
import cors from 'cors';

// Import custom modules
import { RedisClient } from './utils/cache';
import { logger } from './config/logger';
import { httpLogger } from './config/httpLogger';

// Import routes
import { router } from './routes';


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

    // Parse URL-encoded bodies (for form submissions)
    this.app.use(urlencoded({ extended: true }));

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
