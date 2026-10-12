import { createClient } from 'redis';
import { env } from '../config/env';
import { logger } from '../config/logger';

export class RedisClient {
  static client: ReturnType<typeof createClient>;

  static init() {
    if (this.client) return;

    this.client = createClient({
      url: `redis://${env.REDIS_HOST}:${env.REDIS_PORT}`
    });

    // node-redis emits connection errors separately from the connect promise.
    // An unhandled `error` event can terminate the service process when Redis
    // is restarted, leaving the container up but the HTTP listener gone.
    this.client.on('error', (err) => {
      logger.error({ err }, 'Redis connection error; the client will reconnect');
    });
    this.client.on('reconnecting', () => {
      logger.warn('Redis connection lost; reconnecting');
    });
    this.client.on('ready', () => {
      logger.info('🔌 Connected to Redis');
    });

    void this.client.connect().catch((err) => {
      logger.error({ err }, 'Initial Redis connection failed');
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
