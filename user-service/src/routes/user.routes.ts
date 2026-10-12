import express from 'express';
import { UserController } from '@/controllers/user.controller';

const router = express.Router();

router.get('/profile', UserController.getProfile);
router.put('/profile', UserController.updateProfile);

export default router;
