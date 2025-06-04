import * as fs from 'fs/promises';
import * as path from 'path';
import { DateTime } from 'luxon';
import { Injectable } from '@nestjs/common';
import { OpenAI } from 'openai'; // 假设你用的是 openai SDK

@Injectable()
export class ChatService {
  private readonly openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
  private readonly historyDir = path.join(__dirname, '..', '..', 'history');

  async chatWithGPT(phoneNumber: string, content: string): Promise<{ response: string }> {
    if (!phoneNumber || !content) {
      console.warn('Missing phoneNumber or content');
      return { response: 'Invalid input: phone number and message content are required.' };
    }

    const userId = phoneNumber.replace(/\W/g, '') || 'anonymous';
    const historyFile = path.join(this.historyDir, `${userId}.txt`);
    const userLine = `[User @ ${DateTime.now().toISO()}]: ${content}\n`;

    try {
      await fs.mkdir(this.historyDir, { recursive: true });
      await fs.appendFile(historyFile, userLine);

      const historyText = await fs.readFile(historyFile, 'utf-8');
      const prompt = `Below is the conversation history. Continue the chat naturally.\n\n${historyText}\n[Assistant]:`;

      const chat = await this.openai.chat.completions.create({
        messages: [{ role: 'user', content: prompt }],
        model: 'gpt-3.5-turbo',
      });

      const reply = chat.choices[0]?.message?.content || 'Sorry, something went wrong.';
      const assistantLine = `[Assistant @ ${DateTime.now().toISO()}]: ${reply}\n`;
      await fs.appendFile(historyFile, assistantLine);

      return { response: reply };
    } catch (err) {
      console.error('GPT API error:', err);
      return { response: 'An error occurred while processing your request.' };
    }
  }
}
