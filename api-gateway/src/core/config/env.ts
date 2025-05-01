import dotenv from 'dotenv';
import { z } from 'zod';

// Load environment variables from .env file
dotenv.config();

// Define schema for environment variables
const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
  API_GATEWAY_PORT: z.string().transform(val => Number(val)).refine(p => !isNaN(p) && p > 0, {
    message: 'API_GATEWAY_PORT must be a positive number',
  }),
  REDIS_PORT: z.string().transform(val => Number(val)).refine(p => !isNaN(p) && p > 0, {
    message: 'REDIS_PORT must be a positive number',
  }),
  JWT_SECRET: z.string().min(10, 'JWT_SECRET must be at least 10 characters'),
  USER_SERVICE_URL: z.string().url(),
  REDIS_HOST: z.string().min(1, 'REDIS_HOST is required'),
  INTERNAL_API_KEY: z.string().min(10, 'INTERNAL_API_KEY is required'),
});

// Parse and validate the environment variables
const _env = envSchema.safeParse(process.env);

if (!_env.success) {
  console.error('❌ Invalid environment variables:\n', _env.error.format());
  process.exit(1); // Exit the process if environment variables are invalid
}


// Export validated environment variables
export const env = _env.data;
