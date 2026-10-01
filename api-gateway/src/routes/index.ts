import { Router } from 'express';
import userRoutes from './user.routes';
import authRoutes from './auth.routes';
import contentRoutes from './content.routes';
import publicContentRoutes from './public-content.routes';
import { authenticate } from '@/core/middlewares/auth.middleware';

const router = Router();

router.use('/auth', authRoutes);
router.use('/users', authenticate, userRoutes);
// Published videos are intentionally public. Upload and personal job-state APIs
// remain behind authentication below.
router.use('/content', publicContentRoutes);
router.use('/content', authenticate, contentRoutes);

export default router;
