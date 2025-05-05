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
        try {
            const userId = req.params.id;
            const updatedData = req.body;
            // Simulate updating user profile in database
            const updatedProfile = {
                id: userId,
                ...updatedData,
            };
            res.status(200).json({ message: "Profile updated successfully", updatedProfile });
        } catch (error) {
            res.status(500).json({ message: "Failed to update user profile", error });
        }
    }

}



