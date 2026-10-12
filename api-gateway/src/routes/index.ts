import { Router } from 'express';
import userRoutes from './user.routes';
import authRoutes from './auth.routes';
import contentRoutes from './content.routes';
import publicContentRoutes from './public-content.routes';
import { authenticate } from '@/core/middlewares/auth.middleware';

const router = Router();

router.use('/auth', authRoutes);
router.use('/users', authenticate, userRoutes);
// Published catalogue browsing is public. Playback-session creation, uploads,
// and personal video-management APIs require authentication.
router.use('/content', publicContentRoutes);
router.use('/content', authenticate, contentRoutes);

export default router;
