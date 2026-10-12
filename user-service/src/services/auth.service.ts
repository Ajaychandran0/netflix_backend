import { hash, compare } from 'bcrypt';
import { prisma } from '../core/db/prisma';
import { generateToken } from '../core/utils/jwt';
import { BadRequestError } from '@/core/errors/BadRequestError';
import { NotFoundError } from '@/core/errors/NotFoundError';
import { ErrorCodes } from '@/core/constants/ResponseCodes';
import { ResponseMessages } from '@/core/constants/ResponseMessages';
import { UnauthorizedError } from '@/core/errors/UnauthorizedError';

export class UserService {
  static async register(email: string, password: string): Promise<string> {
    const existingUser = await prisma.user.findUnique({ where: { email } });
    if (existingUser) {
      throw new BadRequestError(ResponseMessages.USER_ALREADY_EXISTS, ErrorCodes.USER_ALREADY_EXISTS);
    }

    const hashedPassword = await hash(password, 10);
    const user = await prisma.user.create({
      data: {
        email,
        password: hashedPassword,
      },
    })

    const token = generateToken({ id: user.id, email: user.email, role: user.role });
    return token;
  }

  static async login(email: string, password: string): Promise<string> {
    const user = await prisma.user.findUnique({ where: { email } });
    if (!user) {
      throw new NotFoundError(ResponseMessages.USER_NOT_FOUND, ErrorCodes.USER_NOT_FOUND);
    }

    const isPasswordValid = await compare(password, user.password);
    if (!isPasswordValid) {
      throw new UnauthorizedError(ResponseMessages.INVALID_CREDENTIALS, ErrorCodes.INVALID_CREDENTIALS);
    }

    const token = generateToken({ id: user.id, email: user.email, role: user.role });
    return token;
  }
}
