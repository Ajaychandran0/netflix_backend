import express from 'express';
import { baseService } from '@/services/base.service';
import { authenticate } from '@/core/middlewares/auth.middleware';

const router = express.Router();

router.get('/profile', baseService.forward('user-service', 'get', '/api/users/profile'));
router.put('/update', baseService.forward('user-service', 'put', '/api/users/update'));

export default router;
