import { Router } from 'express';

export const router = Router();

router.get('/health', (req, res) => {
  res.send({ code: "SUCCESS", message: 'API Gateway running' });
});

// Later: /home, /login, etc.
