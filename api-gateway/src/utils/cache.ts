import { createClient } from 'redis';
import { env } from '../config/env';
import { logger } from '../config/logger';

export class RedisClient {
  static client: ReturnType<typeof createClient>;

  static init() {
    this.client = createClient({
      url: `redis://${env.REDIS_HOST}:${env.REDIS_PORT}`
    });

    this.client.connect().then(() => {
      logger.info('🔌 Connected to Redis');
    }).catch((err) => {
      logger.error('❌ Error connecting to Redis:', err);
    });
  }

  static async get<T = any>(key: string): Promise<T | null> {
    const value = await this.client.get(key);
    return value ? JSON.parse(value) as T : null;
  }

  static async set<T>(key: string, value: T, ttl = 3600) {
    await this.client.setEx(key, ttl, JSON.stringify(value));
  }

  static async del(key: string): Promise<number> {
    return await this.client.del(key);
  }
}
