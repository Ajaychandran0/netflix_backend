import express from 'express';
import { baseService } from '@/services/base.service';

const router = express.Router();

router.get('/profile', (req, res, next) => {
    // Profile data is tied to the current bearer token. Never let a cached
    // representation (or its validators) cross logout/login boundaries.
    delete req.headers['if-none-match'];
    delete req.headers['if-modified-since'];
    res.setHeader('Cache-Control', 'no-store');
    next();
}, baseService.forward('user-service', 'get', '/api/users/profile'));
router.put('/profile', baseService.forward('user-service', 'put', '/api/users/profile'));

export default router;
