import express from 'express';
import { UserController } from '@/controllers/user.controller';

const router = express.Router();

router.get('/profile', UserController.getProfile);
router.post('/signin', UserController.updateProfile);

export default router;
