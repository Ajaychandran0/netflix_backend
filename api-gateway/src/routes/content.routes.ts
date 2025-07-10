import express from 'express';
import { baseService } from '@/services/base.service';

const router = express.Router();

router.post('/initiate_upload', baseService.forward('content-service', 'post', '/api/content/initiate_upload'));
router.post('/complete_upload', baseService.forward('content-service', 'post', '/api/content/complete_upload'));

export default router;
