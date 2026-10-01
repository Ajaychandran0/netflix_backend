import express from 'express';
import { baseService } from '@/services/base.service';

const router = express.Router();

router.get('/videos', baseService.forward('content-service', 'get', '/api/content/videos/'));
router.get(
    '/videos/:videoId/playback',
    baseService.forward(
        'content-service',
        'get',
        (req) => `/api/content/videos/${req.params.videoId}/playback`,
    ),
);

export default router;
