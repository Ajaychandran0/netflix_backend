import { Request, Response } from 'express';
import { UserService } from '../services/auth.service';

export class AuthController {
  static async register(req: Request, res: Response): Promise<void> {
    const { email, password, subscriptionPlanId } = req.body;
    try {
      const token = await UserService.register(email, password, subscriptionPlanId);
      res.status(201).json({ token });
    } catch (error: unknown) {
      if (error instanceof Error) {
        res.status(400).json({ message: error.message });
      } else {
        res.status(400).json({ message: 'An unexpected error occurred' });
      }
    }
  }

  static async login(req: Request, res: Response): Promise<void> {
    const { email, password } = req.body;
    try {
      const token = await UserService.login(email, password);
      res.status(200).json({ token });
    } catch (error: unknown) {
      if (error instanceof Error) {
        res.status(400).json({ message: error.message });
      } else {
         res.status(400).json({ message: 'An unexpected error occurred' });
      }
    }
  }
}
