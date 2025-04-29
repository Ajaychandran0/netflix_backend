import express, { Application } from 'express';
import cors from 'cors';
import { json, urlencoded } from 'body-parser';
import authRoutes  from './routes/auth.routes';
// import { userRoutes } from './routes/user.routes';

export class App {
  public app: Application;

  constructor() {
    this.app = express();
    this.configureMiddleware();
    this.configureRoutes();
  }

  // Configure middleware for the app
  private configureMiddleware(): void {
    this.app.use(cors());
    this.app.use(json());
    this.app.use(urlencoded({ extended: true }));
  }

  // Configure routes for the app
  private configureRoutes(): void {
    this.app.use('/api/auth', authRoutes);
    // this.app.use('/api/users', userRoutes);
  }

  // Start the app
  public listen(port: number): void {
    this.app.listen(port, () => {
      console.log(`User Service running on port ${port}`);
    });
  }
}
