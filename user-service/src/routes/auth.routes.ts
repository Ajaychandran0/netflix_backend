import { Router } from 'express';

const router = Router();

router.get('/health', (_req, res) => {
    res.send({ status: 'API Gateway running' });
});

// Later: /home, /login, etc.

export default router