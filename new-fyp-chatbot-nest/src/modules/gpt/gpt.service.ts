import * as fs from 'fs/promises';
import { Injectable, Logger } from '@nestjs/common';
import { OpenAI } from 'openai';
import { ExerciseSummaryService } from '../exercise/exercise_summary.service';
import { SupabaseService } from '../supabase/supabase.service';
import { RedisService } from '../redis/redis.service';
import * as crypto from 'crypto';

@Injectable()
export class ChatService {
  private readonly logger = new Logger(ChatService.name);
  private readonly openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

  constructor(
    private readonly exerciseSummaryService: ExerciseSummaryService,
    private readonly supabaseService: SupabaseService,
    private readonly redisService: RedisService,
  ) {}

  async chatWithGPT(phoneNumber: string, content: string): Promise<{ response: string }> {
    this.logger.log(`🔍 [GPT Service] Starting request processing - Phone: ${phoneNumber}, Content: ${content.substring(0, 50)}...`);

    if (!phoneNumber || !content) {
      this.logger.warn('❌ [GPT Service] Missing phone number or content');
      return { response: 'Invalid input: phone number and message content are required.' };
    }

    // 生成查询哈希，用于缓存相同查询
    const queryHash = this.generateQueryHash(phoneNumber, content);

    // 1. 检查缓存的GPT响应
    try {
      const cachedResponse = await this.redisService.getGPTResponse(queryHash);
      if (cachedResponse) {
        this.logger.log('✅ [GPT Service] Returning cached GPT response');
        return { response: cachedResponse };
      }
    } catch (cacheError) {
      this.logger.warn('⚠️ [GPT Service] Cache read failed, proceeding without cache:', cacheError.message);
    }

    // 2. Find profileId
    let profileId: string | null = null;
    try {
      this.logger.log(`🔍 [GPT Service] Finding user ID for phone: ${phoneNumber}`);
      profileId = (await this.supabaseService.getUserIdByPhone(phoneNumber))?.toString();
      this.logger.log(`✅ [GPT Service] Found user ID: ${profileId}`);
    } catch (e) {
      this.logger.error(`❌ [GPT Service] Failed to find user ID: ${e.message}`);
    }

    let weeklyReport = '';
    if (profileId) {
      // 3. 尝试从缓存获取周报
      try {
        let cachedReport = await this.redisService.getWeeklyReport(profileId);
        if (cachedReport) {
          weeklyReport = cachedReport;
          this.logger.log('✅ [GPT Service] Using cached weekly report');
        } else {
          // 从数据库获取并缓存
          this.logger.log(`📊 [GPT Service] Getting weekly report for user ID: ${profileId}`);
          weeklyReport = await this.exerciseSummaryService.getWeeklyProgressMessage(profileId);

          // 缓存周报
          await this.redisService.cacheWeeklyReport(profileId, weeklyReport);
          this.logger.log('💾 [GPT Service] Weekly report cached');
        }
        this.logger.log(`✅ [GPT Service] Weekly report content: ${weeklyReport.substring(0, 100)}...`);
      } catch (e) {
        this.logger.error(`❌ [GPT Service] Failed to get weekly report: ${e.message}`);
      }
    } else {
      this.logger.log(`⚠️ [GPT Service] User ID not found, cannot get weekly report`);
    }

    // 4. Construct prompt
    const prompt = `
    // User's historical exercise information is as follows:
    // ${weeklyReport}

    // User's question is as follows:
    // ${content}

    Please provide a targeted suggestion or reply based on the user's historical exercise information. If no historical data is available, provide general health and exercise advice without mentioning the lack of data. Never say "no historical data" or similar phrases.`;

    this.logger.log(`🤖 [GPT Service] Prompt sent to GPT: ${prompt.substring(0, 200)}...`);

    try {
      const chat = await this.openai.chat.completions.create({
        messages: [{ role: 'user', content: prompt }],
        model: 'gpt-4',
        temperature: 0.7,
      });

      const reply = chat.choices[0]?.message?.content || 'Sorry, something went wrong.';
      this.logger.log(`✅ [GPT Service] GPT reply: ${reply.substring(0, 100)}...`);

      // 5. 缓存GPT响应
      try {
        await this.redisService.cacheGPTResponse(queryHash, reply);
        this.logger.log('💾 [GPT Service] GPT response cached');
      } catch (cacheError) {
        this.logger.warn('⚠️ [GPT Service] Failed to cache GPT response:', cacheError.message);
      }

      return { response: reply };
    } catch (err) {
      this.logger.error('❌ [GPT Service] GPT API error:', err);
      return { response: 'An error occurred while processing your request.' };
    }
  }

  // 生成查询哈希（用于缓存相同查询）
  private generateQueryHash(phoneNumber: string, content: string): string {
    const hashInput = `${phoneNumber}:${content.trim().toLowerCase()}`;
    return crypto.createHash('md5').update(hashInput).digest('hex');
  }

  async generateProactiveMessage(phoneNumber: string, type: 'inactivity' | 'intensity', data: any): Promise<string> {
    this.logger.log(`🤖 [GPT Service] Generating proactive message for ${type}`);

    const prompt = type === 'inactivity' 
      ? `The patient hasn't exercised in ${data.days} days. Write a short, encouraging, and friendly WhatsApp message (max 30 words) to remind them to stay active. Mention that consistency is key!`
      : `The patient just finished a workout. Their average heart rate was ${data.avgHR} bpm, which is slightly below their target of ${data.target} bpm. Write a supportive message (max 30 words) praising their effort but gently suggesting they increase intensity next time.`;

    try {
      const chat = await this.openai.chat.completions.create({
        messages: [{ role: 'user', content: prompt }],
        model: 'gpt-4', // Or 'gpt-3.5-turbo' if you want to save money
        temperature: 0.8, // A bit higher for more "creative/friendly" tone
      });

      return chat.choices[0]?.message?.content || 'Keep up the great work!';
    } catch (err) {
      this.logger.error('❌ [GPT Service] OpenAI Error:', err);
      return "Just a friendly reminder to keep moving and stay healthy!";
    }
  }
}
