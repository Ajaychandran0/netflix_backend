import express from 'express';
import { signup, signin } from '../services/user.service';

const router = express.Router();

router.post('/register', signup);
router.post('/signin', signin);

export default router;
