import express from 'express';
import { getProfile, updateProfile } from '../services/user.service';

const router = express.Router();

router.get('/profile', getProfile);
router.put('/update', updateProfile);

export default router;
