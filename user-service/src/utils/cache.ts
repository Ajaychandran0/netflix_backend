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

  static async get(key: string) {
    return await this.client.get(key);
  }

  static async set(key: string, value: string, ttl = 3600) {
    await this.client.setEx(key, ttl, value);
  }

  static async del(key: string) {
    await this.client.del(key);
  }
}
