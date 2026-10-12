import { SuccessCodes } from '@/core/constants/ResponseCodes';
import { prisma } from '@/core/db/prisma';
import { UserNotFoundError } from '@/core/errors/NotFoundError';
import { apiResponse } from '@/core/utils/apiResponse';
import { Request, Response } from 'express';


export class UserController {
    static async getProfile(req: Request, res: Response): Promise<void> {
        const user = await prisma.user.findUnique({
            where: {
                id: req.user?.id,
            },
        });

        if (!user) {
            throw new UserNotFoundError();
        }

        const { password, ...safeUser } = user;

        apiResponse({
            res,
            message: "User profile fetched successfully",
            data: safeUser,
            code: SuccessCodes.USER_FETCHED,
        })
    }

    static async updateProfile(req: Request, res: Response): Promise<void> {
        const user = await prisma.user.findUnique({
            where: { id: req.user?.id }
        })

        if (!user) {
            throw new UserNotFoundError()
        }

        const updatedUser = await prisma.user.update({
            where: { id: req.user?.id },
            data: {
                firstName: req.body.firstName ?? user.firstName,
                lastName: req.body.lastName ?? user.lastName,
            }
        })

        const { password, ...safeUser } = updatedUser

        apiResponse({
            res,
            message: "User profile updated successfully",
            data: safeUser,
            code: SuccessCodes.USER_UPDATED,
        })

    }

}



