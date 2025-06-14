import * as fs from 'fs/promises';
import { Injectable } from '@nestjs/common';
import { OpenAI } from 'openai';

@Injectable()
export class ChatService {
  private readonly openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

  async chatWithGPT(phoneNumber: string, content: string): Promise<{ response: string }> {
    if (!phoneNumber || !content) {
      console.warn('Missing phoneNumber or content');
      return { response: 'Invalid input: phone number and message content are required.' };
    }

    // 尝试解析 content 为 JSON（传进来的应是病人信息）
    let patient: {
      name: string;
      age: number;
      condition: string;
      appointment: string;
      doctor: string;
    };

    try {
      patient = JSON.parse(content);
    } catch (e) {
      return { response: 'Invalid input format: content must be a valid JSON string.' };
    }

    const prompt = `
Generate a polite and informative reminder message for the following patient:
Name: ${patient.name}
Age: ${patient.age}
Condition: ${patient.condition}
Next Appointment: ${patient.appointment}
Doctor: ${patient.doctor}

The message should be clear, friendly, and appropriate for WhatsApp message format.
`;

    try {
      const chat = await this.openai.chat.completions.create({
        messages: [{ role: 'user', content: prompt }],
        model: 'gpt-4',
        temperature: 0.7,
      });

      const reply = chat.choices[0]?.message?.content || 'Sorry, something went wrong.';
      return { response: reply };
    } catch (err) {
      console.error('GPT API error:', err);
      return { response: 'An error occurred while processing your request.' };
    }
  }
}
