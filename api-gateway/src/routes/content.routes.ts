import express from 'express';
import { baseService } from '@/services/base.service';

const router = express.Router();

router.post('/initiate_upload', baseService.forward('content-service', 'post', '/api/content/initiate_upload'));
router.post('/complete_upload', baseService.forward('content-service', 'post', '/api/content/complete_upload'));
router.get('/videos/mine', baseService.forward('content-service', 'get', '/api/content/videos/mine'));
router.get(
    '/videos/:videoId/playback',
    baseService.forward(
        'content-service',
        'get',
        (req) => `/api/content/videos/${req.params.videoId}/playback`,
    ),
);
router.get(
    '/videos/:videoId/progress',
    baseService.forward(
        'content-service',
        'get',
        (req) => `/api/content/videos/${req.params.videoId}/progress`,
    ),
);
router.put(
    '/videos/:videoId',
    baseService.forward('content-service', 'put', (req) => `/api/content/videos/${req.params.videoId}`),
);
router.delete(
    '/videos/:videoId',
    baseService.forward('content-service', 'delete', (req) => `/api/content/videos/${req.params.videoId}`),
);

export default router;
