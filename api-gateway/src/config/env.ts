// api-gateway/src/config/env.ts

import dotenv from 'dotenv';
dotenv.config();

const required = (value: string | undefined, name: string): string => {
  if (!value) throw new Error(`Missing required env var: ${name}`);
  return value;
};

export const env = {
  PORT: parseInt(required(process.env.PORT, 'PORT')),
  JWT_SECRET: required(process.env.JWT_SECRET, 'JWT_SECRET'),
  USER_SERVICE_URL: required(process.env.USER_SERVICE_URL, 'USER_SERVICE_URL'),
  AUTH_SERVICE_URL: required(process.env.AUTH_SERVICE_URL, 'AUTH_SERVICE_URL'),
  CONTENT_SERVICE_URL: required(process.env.CONTENT_SERVICE_URL, 'CONTENT_SERVICE_URL'),
  REDIS_URL: required(process.env.REDIS_URL, 'REDIS_URL'),
  API_KEY: required(process.env.API_KEY, 'API_KEY'), // optional if using API key validation between services
};
