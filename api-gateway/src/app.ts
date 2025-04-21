import express, { Application } from 'express';
import { createClient } from 'redis';
import { router } from './routes';
import { AuthMiddleware } from './middlewares/auth.middleware';
import { RedisClient } from './utils/cache';

export class App {
  public app: Application;

  constructor() {
    this.app = express();
    this.config();
    this.routes();
  }

  private config(): void {
    this.app.use(express.json());

    // Init Redis connection
    RedisClient.init();

    // Auth Middleware globally
    this.app.use(AuthMiddleware);
  }

  private routes(): void {
    this.app.use('/', router);
  }

  public listen(port: string | number): void {
    this.app.listen(port, () => {
      console.log(`API Gateway running on port ${port}`);
    });
  }
}
