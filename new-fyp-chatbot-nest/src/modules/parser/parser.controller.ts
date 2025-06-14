import {
  Controller,
  Post,
  UploadedFiles,
  UseInterceptors,
  BadRequestException,
} from '@nestjs/common';
import { FilesInterceptor } from '@nestjs/platform-express';
import { ParserService } from './parser.service';
import { SupabaseService } from '../supabase/supabase.service';
import { ChatService } from '../gpt/gpt.service';
import axios from 'axios';
import * as fs from 'fs/promises';
import { Logger } from '@nestjs/common';

@Controller('parser')
export class ParserController {
  private readonly logger = new Logger(ParserController.name);

  constructor(
    private readonly parserService: ParserService,
    private readonly supabaseService: SupabaseService,
    private readonly chatService: ChatService,
  ) {}

  @Post('upload-and-send')
  @UseInterceptors(FilesInterceptor('files', 1))
  async uploadAndSend(@UploadedFiles() files: Express.Multer.File[]) {
    if (!files || files.length === 0) {
      throw new BadRequestException('No file uploaded');
    }

    const file = files[0];
    const content = file.buffer.toString('utf-8');
    this.logger.log(`📄 Received file: ${file.originalname}`);

    const patientList = await this.parserService.extractMultiplePatientsFromTxt(content);
    this.logger.log(`📊 Parsed ${patientList.length} patient records`);

    const results = [];

    for (const { phone, patient } of patientList) {
      try {
        this.logger.log(`📞 Processing phone: ${phone}`);

        // 调用 GPT 生成消息
        const gptResponse = await this.chatService.chatWithGPT(phone, JSON.stringify(patient));
        this.logger.log(`🧠 GPT response ready for ${phone}`);

        // 获取 Supabase 中患者 ID
        const userId = await this.supabaseService.getUserIdByPhone(phone);
        if (userId) {
          await this.supabaseService.insertChatHistory(
            userId.toString(),
            'assistant',
            gptResponse.response,
          );
          this.logger.log(`📝 Chat history saved for ${phone}`);
        } else {
          this.logger.warn(`⚠️ Supabase: No userId found for ${phone}`);
        }

        // 调用 Flask Bot 发 WhatsApp 消息
        const res = await axios.post('http://localhost:5000/send/', {
          to: phone,
          body: gptResponse.response,
        });

        results.push({
          phone,
          status: 'sent',
          message: gptResponse.response,
          sid: res.data.sid || null,
        });

        this.logger.log(`✅ WhatsApp message sent to ${phone}`);
      } catch (err) {
        this.logger.error(`❌ Failed to process ${phone}: ${err.message}`);
        results.push({
          phone,
          status: 'failed',
          error: err.message,
        });
      }
    }

    return {
      total: results.length,
      results,
    };
  }
}
