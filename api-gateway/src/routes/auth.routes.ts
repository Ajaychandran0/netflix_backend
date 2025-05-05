import express from 'express';
import { baseService } from '@/services/base.service';

const router = express.Router();

router.post('/register', baseService.forward('user-service', 'post', '/api/auth/register'));
router.post('/signin', baseService.forward('user-service', 'post', '/api/auth/signin'));

export default router;
