import express from 'express';
import { baseService } from '@/services/base.service';

const router = express.Router();

router.get('/profile', baseService.forward('user-service', 'get', '/api/users/profile'));
router.put('/profile', baseService.forward('user-service', 'put', '/api/users/profile'));

export default router;
