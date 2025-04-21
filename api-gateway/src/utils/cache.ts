import { createClient } from 'redis';

export class RedisClient {
static client: ReturnType<typeof createClient>;

  static init() {
    this.client = createClient({
      url: `redis://${process.env.REDIS_HOST}:${process.env.REDIS_PORT}`
    });

    this.client.connect().then(() => {
      console.log('🔌 Connected to Redis');
    }).catch(console.error);
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
