// src/routes/authRoutes.ts
import express from 'express';
import { AuthController } from '../controllers/auth.controller';

const router = express.Router();

router.post('/register', AuthController.register);
router.post('/login', AuthController.login);

export default router;
