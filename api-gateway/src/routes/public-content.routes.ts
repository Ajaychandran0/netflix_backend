import express from 'express';
import { baseService } from '@/services/base.service';

const router = express.Router();

router.get('/videos', baseService.forward('content-service', 'get', '/api/content/videos/'));

export default router;
