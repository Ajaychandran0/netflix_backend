import { Router } from 'express';
import userRoutes from './user.routes';
import authRoutes from './auth.routes';
import { requireUser } from '@/core/middlewares/authHandler';

const router = Router();

router.use('/auth', authRoutes);
router.use('/users', requireUser, userRoutes);

export default router;