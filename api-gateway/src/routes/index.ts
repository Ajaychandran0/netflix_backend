import { Router } from 'express';
import userRoutes from './user.routes';
import authRoutes from './auth.routes';
import contentRoutes from './content.routes';
import { authenticate } from '@/core/middlewares/auth.middleware';

const router = Router();

router.use('/auth', authRoutes);
router.use('/users', authenticate, userRoutes);
router.use('/content', authenticate, contentRoutes)

export default router;