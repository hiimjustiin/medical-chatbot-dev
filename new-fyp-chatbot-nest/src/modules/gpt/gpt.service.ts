import * as fs from 'fs/promises';
import { Injectable } from '@nestjs/common';
import { OpenAI } from 'openai';
import { ExerciseSummaryService } from '../exercise/exercise_summary.service';
import { SupabaseService } from '../supabase/supabase.service';

@Injectable()
export class ChatService {
  private readonly openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

  constructor(
    private readonly exerciseSummaryService: ExerciseSummaryService,
    private readonly supabaseService: SupabaseService,
  ) {}

  async chatWithGPT(phoneNumber: string, content: string): Promise<{ response: string }> {
    console.log(`🔍 [GPT Service] Starting request processing - Phone: ${phoneNumber}, Content: ${content}`);
    
    if (!phoneNumber || !content) {
      console.warn('❌ [GPT Service] Missing phone number or content');
      return { response: 'Invalid input: phone number and message content are required.' };
    }

    // 1. Find profileId
    let profileId: string | null = null;
    try {
      console.log(`🔍 [GPT Service] Finding user ID for phone: ${phoneNumber}`);
      profileId = (await this.supabaseService.getUserIdByPhone(phoneNumber))?.toString();
      console.log(`✅ [GPT Service] Found user ID: ${profileId}`);
    } catch (e) {
      console.error(`❌ [GPT Service] Failed to find user ID: ${e.message}`);
    }
    
    let weeklyReport = '';
    if (profileId) {
      try {
        console.log(`📊 [GPT Service] Getting weekly report for user ID: ${profileId}`);
        weeklyReport = await this.exerciseSummaryService.getWeeklyProgressMessage(profileId);
        console.log(`✅ [GPT Service] Weekly report content: ${weeklyReport.substring(0, 100)}...`);
      } catch (e) {
        console.error(`❌ [GPT Service] Failed to get weekly report: ${e.message}`);
      }
    } else {
      console.log(`⚠️ [GPT Service] User ID not found, cannot get weekly report`);
    }

    // 2. Construct prompt
    const prompt = `
User's historical exercise information is as follows:
${weeklyReport || 'No historical exercise data available.'}

User's question is as follows:
${content}

Please provide a targeted suggestion or reply based on the user's historical exercise information.`;

    console.log(`🤖 [GPT Service] Prompt sent to GPT: ${prompt.substring(0, 200)}...`);

    try {
      const chat = await this.openai.chat.completions.create({
        messages: [{ role: 'user', content: prompt }],
        model: 'gpt-4',
        temperature: 0.7,
      });

      const reply = chat.choices[0]?.message?.content || 'Sorry, something went wrong.';
      console.log(`✅ [GPT Service] GPT reply: ${reply.substring(0, 100)}...`);
      return { response: reply };
    } catch (err) {
      console.error('❌ [GPT Service] GPT API error:', err);
      return { response: 'An error occurred while processing your request.' };
    }
  }
}
