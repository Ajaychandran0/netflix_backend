import { Request, Response } from 'express';
import { UserService } from '../services/auth.service';
import { SuccessCodes } from '@/core/constants/ResponseCodes';
import { apiResponse } from '@/core/utils/apiResponse';
import { ResponseMessages } from '@/core/constants/ResponseMessages';

export class AuthController {
  static async register(req: Request, res: Response): Promise<void> {
    const { email, password } = req.body;
    const token = await UserService.register(email, password);
    apiResponse({
      res,
      message: ResponseMessages.USER_CREATED,
      statusCode: 201,
      data: { token },
      code: SuccessCodes.USER_CREATED,
      enableLogging: true,
    })
  }

  static async login(req: Request, res: Response): Promise<void> {
    const { email, password } = req.body;
    const token = await UserService.login(email, password);
    apiResponse({
      res,
      message: ResponseMessages.USER_LOGGED_IN,
      data: { token },
      code: SuccessCodes.USER_LOGGED_IN,
      enableLogging: true,
    })
  }
}
