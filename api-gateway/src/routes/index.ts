import { Router } from 'express';

export const router = Router();

router.get('/health', (req, res) => {
  res.send({ status: 'API Gateway running' });
});

// Later: /home, /login, etc.
