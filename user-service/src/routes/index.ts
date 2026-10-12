import { Router } from 'express';
import userRoutes from './user.routes';
import authRoutes from './auth.routes';
import { attachUserFromHeaders } from '@/core/middlewares/attachUserFromHeaders';
import { validateUserHeaders } from '@/core/middlewares/validateUserHeaders';

const router = Router();

router.use('/auth', authRoutes);
router.use('/users',validateUserHeaders, attachUserFromHeaders, userRoutes);

export default router;