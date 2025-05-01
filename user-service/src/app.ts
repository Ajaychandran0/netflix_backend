import express, { Application, NextFunction, Request, Response } from 'express';
import 'express-async-errors';
import { urlencoded } from 'body-parser';
import compression from 'compression';
import helmet from 'helmet';
import cors from 'cors';

// Import custom modules
import { errorHandler } from './core/middlewares/errorHandler';
import { httpLogger } from './core/config/httpLogger';
import { RedisClient } from './core/utils/cache';
import { logger } from './core/config/logger';

// Import routes
import authRoutes from './routes/auth.routes';
// import { userRoutes } from './routes/user.routes';

export class App {
  public app: Application;

  constructor() {
    this.app = express();
    this.config();
    this.routes();
    this.handleErrors();
  }

  // Configure middleware for the app
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

  // Configure routes for the app
  private routes(): void {
    this.app.get("/", (req: Request, res: Response) => {
      res.send({ code: "SUCCESS", message: 'User Service running' });
    })
    this.app.use('/api/auth', authRoutes);
    // this.app.use('/api/users', userRoutes);

  }

  private handleErrors(): void {
    this.app.use((err: unknown, req: Request, res: Response, next: NextFunction) => {
      errorHandler(err, req, res, next);
    });
  }


  // Start the app
  public listen(port: number): void {
    this.app.listen(port, () => {
      logger.info(`User Service running on port ${port}`);
    });
  }
}
