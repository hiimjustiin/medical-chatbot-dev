import {
  Controller,
  Post,
  UploadedFiles,
  UseInterceptors,
  BadRequestException,
  Body,
} from '@nestjs/common';
import { FilesInterceptor } from '@nestjs/platform-express';
import { ParserService } from '../parser/parser.service';
import { SupabaseService } from '../supabase/supabase.service';
import { ChatService } from '../gpt/gpt.service'; // ← 改这个
import axios from 'axios';

@Controller('parser')
export class ParserController {
  constructor(
    private readonly parserService: ParserService,
    private readonly supabaseService: SupabaseService,
    private readonly chatService: ChatService,
  ) {}

  // ✅ 接口 1：结构化上传（已有逻辑）
  @Post('parse-and-upload')
  @UseInterceptors(FilesInterceptor('files', 50))
  async parseAndUpload(
    @UploadedFiles() files: Express.Multer.File[],
    @Body('profileID') profileID: string,
  ) {
    console.log(profileID);
    if (!files || files.length === 0) {
      throw new BadRequestException('No files uploaded');
    }

    if (!profileID) {
      throw new BadRequestException('Profile ID is required');
    }

    const allParsedRecords = [];

    try {
      for (const file of files) {
        const fileContent = file.buffer.toString('utf-8');
        const parsedRecords = this.parserService.parseTextFileContent(
          fileContent,
          profileID,
        );
        allParsedRecords.push(...parsedRecords);
      }

      const savedRecords =
        await this.supabaseService.insertParsedRecords(allParsedRecords);
      return { success: true, savedRecords };
    } catch (error) {
      console.error('Error parsing files:', error);
      throw new BadRequestException('Failed to parse and upload files');
    }
  }

  // ✅ 接口 2：上传文档 → GPT 生成消息 → 发 WhatsApp
  @Post('upload-and-send')
  @UseInterceptors(FilesInterceptor('files', 1))
  async uploadAndSend(
    @UploadedFiles() files: Express.Multer.File[],
    @Body('userId') userId: string,
    @Body('phone') phone: string,
  ) {
    if (!files || files.length === 0) {
      throw new BadRequestException('No file uploaded');
    }
    if (!userId || !phone) {
      throw new BadRequestException('User ID and phone number are required');
    }

    const file = files[0];
    const fileContent = file.buffer.toString('utf-8');

    const summaryPrompt = `Please generate a health report summary suitable for sending via WhatsApp based on the following exercise record text. The language should be friendly and gentle, and no more than 80 words：\n\n${fileContent}`;

    const gptResponse = await this.chatService.chatWithGPT(
      userId,
      summaryPrompt,
    );

    // ✅ 实际调用 Flask 的 WhatsApp Bot 接口
    try {
      const res = await axios.post('http://localhost:5000/send/', {
        to: phone,
        body: gptResponse.response,
      });

      return {
        success: true,
        message: gptResponse.response,
        twilioStatus: res.data.status,
        sid: res.data.sid,
      };
    } catch (err) {
      console.error('❌ WhatsApp sending fails:', err);
      return {
        success: false,
        message: gptResponse.response,
        error: err.message,
      };
    }
  }
}
// 以上代码实现了两个主要功能：
// 1. 接收上传的文件，解析内容并保存到 Supabase 数据库。
// 2. 接收上传的文件内容，生成健康报告摘要，并通过 WhatsApp 发送给指定用户。  