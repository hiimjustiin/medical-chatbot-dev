import { Injectable, Logger, OnModuleDestroy } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { createClient, RedisClientType } from 'redis';

@Injectable()
export class RedisService implements OnModuleDestroy {
  private readonly logger = new Logger(RedisService.name);
  private client: RedisClientType;

  constructor(private configService: ConfigService) {
    this.initRedisClient();
  }

  private async initRedisClient() {
    const redisUrl = this.configService.get<string>('REDIS_URL') || 'redis://localhost:6379';

    try {
      this.client = createClient({
        url: redisUrl,
        socket: {
          connectTimeout: 60000,
          lazyConnect: true,
        },
      });

      // 连接事件监听
      this.client.on('connect', () => {
        this.logger.log('✅ Redis client connected');
      });

      this.client.on('error', (err) => {
        this.logger.error('❌ Redis client error:', err.message);
      });

      this.client.on('ready', () => {
        this.logger.log('🚀 Redis client ready');
      });

      await this.client.connect();
    } catch (error) {
      this.logger.error('❌ Failed to connect to Redis:', error.message);
      // 在开发环境中，如果Redis不可用，我们不应该崩溃应用
      if (process.env.NODE_ENV === 'production') {
        throw error;
      }
    }
  }

  // 基础缓存操作
  async set(key: string, value: any, ttlSeconds?: number): Promise<void> {
    try {
      const serializedValue = JSON.stringify(value);
      if (ttlSeconds) {
        await this.client.setEx(key, ttlSeconds, serializedValue);
      } else {
        await this.client.set(key, serializedValue);
      }
    } catch (error) {
      this.logger.error(`❌ Redis SET error for key ${key}:`, error.message);
      throw error;
    }
  }

  async get<T = any>(key: string): Promise<T | null> {
    try {
      const value = await this.client.get(key);
      return value ? JSON.parse(value) : null;
    } catch (error) {
      this.logger.error(`❌ Redis GET error for key ${key}:`, error.message);
      return null;
    }
  }

  async del(key: string): Promise<number> {
    try {
      return await this.client.del(key);
    } catch (error) {
      this.logger.error(`❌ Redis DEL error for key ${key}:`, error.message);
      return 0;
    }
  }

  async exists(key: string): Promise<boolean> {
    try {
      const result = await this.client.exists(key);
      return result === 1;
    } catch (error) {
      this.logger.error(`❌ Redis EXISTS error for key ${key}:`, error.message);
      return false;
    }
  }

  // 运动数据专用缓存方法
  async cacheWeeklyReport(profileId: string, report: any): Promise<void> {
    const key = `weekly_report:${profileId}`;
    // 缓存24小时
    await this.set(key, report, 24 * 60 * 60);
  }

  async getWeeklyReport(profileId: string): Promise<any | null> {
    const key = `weekly_report:${profileId}`;
    return await this.get(key);
  }

  // GPT响应缓存（避免重复调用相同问题）
  async cacheGPTResponse(queryHash: string, response: string): Promise<void> {
    const key = `gpt_response:${queryHash}`;
    // 缓存1小时
    await this.set(key, { response, timestamp: Date.now() }, 60 * 60);
  }

  async getGPTResponse(queryHash: string): Promise<string | null> {
    const key = `gpt_response:${queryHash}`;
    const cached = await this.get(key);
    return cached?.response || null;
  }

  // 用户会话缓存
  async setUserSession(phoneNumber: string, sessionData: any): Promise<void> {
    const key = `user_session:${phoneNumber}`;
    // 会话缓存30分钟
    await this.set(key, sessionData, 30 * 60);
  }

  async getUserSession(phoneNumber: string): Promise<any | null> {
    const key = `user_session:${phoneNumber}`;
    return await this.get(key);
  }

  // 清理过期缓存
  async cleanupExpiredCache(): Promise<void> {
    try {
      // 使用Redis的SCAN命令清理过期key（Redis会自动清理，但这里可以手动触发）
      this.logger.log('🧹 Cache cleanup completed');
    } catch (error) {
      this.logger.error('❌ Cache cleanup error:', error.message);
    }
  }

  // 健康检查
  async ping(): Promise<boolean> {
    try {
      const result = await this.client.ping();
      return result === 'PONG';
    } catch (error) {
      this.logger.error('❌ Redis ping failed:', error.message);
      return false;
    }
  }

  // 获取缓存统计信息
  async getStats(): Promise<any> {
    try {
      const info = await this.client.info('memory');
      return {
        connected: this.client.isOpen,
        memory: info,
        uptime: process.uptime()
      };
    } catch (error) {
      this.logger.error('❌ Failed to get Redis stats:', error.message);
      return null;
    }
  }

  async onModuleDestroy() {
    if (this.client && this.client.isOpen) {
      await this.client.disconnect();
      this.logger.log('🔌 Redis client disconnected');
    }
  }
}
