// user-service/src/config/env.ts

import dotenv from 'dotenv';
dotenv.config();

const required = (value: string | undefined, name: string): string => {
  if (!value) throw new Error(`Missing required env var: ${name}`);
  return value;
};

export const config = {
  PORT: parseInt(required(process.env.PORT, 'PORT')),
  DATABASE_URL: required(process.env.DATABASE_URL, 'DATABASE_URL'),
  JWT_SECRET: required(process.env.JWT_SECRET, 'JWT_SECRET'),
  REDIS_URL: required(process.env.REDIS_URL, 'REDIS_URL'),
};
