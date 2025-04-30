import { hash, compare } from 'bcrypt';
import { prisma } from '../core/db/prisma';
import { generateToken } from '../core/utils/jwt';

export class UserService {
  static async register(email: string, password: string, subscriptionPlanId: number): Promise<string> {
    const existingUser = await prisma.user.findUnique({ where: { email } });
    if (existingUser) {
      throw new Error('Email already in use');
    }

    const hashedPassword = await hash(password, 10);
    const user = await prisma.user.create({
      data: {
        email,
        password: hashedPassword,
        subscriptionPlanId,
        role: 0,
      },
    });

    const token = generateToken({ userId: user.id, email: user.email, role: user.role });
    return token;
  }

  static async login(email: string, password: string): Promise<string> {
    const user = await prisma.user.findUnique({ where: { email } });
    if (!user) {
      throw new Error('User not found');
    }

    const isPasswordValid = await compare(password, user.password);
    if (!isPasswordValid) {
      throw new Error('Invalid credentials');
    }

    const token = generateToken({ userId: user.id, email: user.email, role: user.role });
    return token;
  }
}
