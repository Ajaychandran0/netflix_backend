import express, { Application } from 'express';
import cors from 'cors';
import { json, urlencoded } from 'body-parser';
// import { userRoutes } from './routes/user.routes';
// import { authRoutes } from './routes/auth.routes';

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
    // this.app.use('/api/users', userRoutes);
    // this.app.use('/api/auth', authRoutes);
  }

  // Start the app
  public listen(port: number): void {
    this.app.listen(port, () => {
      console.log(`User Service running on port ${port}`);
    });
  }
}
