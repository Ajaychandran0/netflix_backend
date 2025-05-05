import { Router } from 'express';
import userRoutes from './user.routes';
import authRoutes from './auth.routes';
import { authenticate } from '@/core/middlewares/auth.middleware';

const router = Router();

router.use('/auth', authRoutes);
router.use('/users', authenticate, userRoutes);

export default router;