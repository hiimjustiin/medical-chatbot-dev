import {
  Controller,
  Post,
  UploadedFiles,
  UseInterceptors,
  BadRequestException,
  Body,
} from '@nestjs/common';
import { FilesInterceptor } from '@nestjs/platform-express';
import { ParserService } from './parser.service';
import { SupabaseService } from '../supabase/supabase.service';
import { ExerciseSummaryService } from '../exercise/exercise_summary.service';
import { Logger } from '@nestjs/common';
import axios from 'axios';

@Controller('parser')
export class ParserController {
  private readonly logger = new Logger(ParserController.name);

  constructor(
    private readonly parserService: ParserService,
    private readonly supabaseService: SupabaseService,
    private readonly exerciseSummaryService: ExerciseSummaryService,
  ) {}

  @Post('upload-workout')
  @UseInterceptors(FilesInterceptor('files', 1))
  async uploadWorkout(
    @UploadedFiles() files: Express.Multer.File[],
    @Body('patientId') patientId: string,
    @Body('phone') phone: string,
  ) {
    if (!files || files.length === 0) {
      throw new BadRequestException('No file uploaded');
    }

    if (!patientId && !phone) {
      throw new BadRequestException('Either Patient ID or Phone Number is required');
    }

    const file = files[0];
    const content = file.buffer.toString('utf-8');
    this.logger.log(`📄 Received file: ${file.originalname}`);

    try {
      // 获取患者ID（如果提供了电话号码）
      let actualPatientId = patientId;
      if (!actualPatientId && phone) {
        actualPatientId = (await this.supabaseService.getUserIdByPhone(phone))?.toString();
        if (!actualPatientId) {
          throw new BadRequestException('Patient not found with the provided phone number');
        }
      }

      // 解析运动数据
      const workoutData = await this.parserService.parseWorkoutData(content);
      this.logger.log(`📊 Parsed ${workoutData.length} workout records`);

      // 合并同一天的数据
      const grouped = this.parserService.groupWorkoutsByDay(workoutData);
      this.logger.log(`📅 Grouped into ${grouped.length} day(s)`);

      // 批量处理
      const results = await this.parserService.processWorkoutsBatch(grouped, actualPatientId);

      // 获取患者信息
      const patient = await this.supabaseService.getPatientById(actualPatientId);
      if (!patient) {
        throw new BadRequestException('Patient not found');
      }

      // 获取周报
      const weeklyMessage = await this.exerciseSummaryService.getWeeklyProgressMessage(actualPatientId);

      // 发送 WhatsApp 消息
      if (patient.phone_number) {
        try {
          await axios.post('http://localhost:5000/send', {
            to: patient.phone_number,
            body: weeklyMessage
          });
          this.logger.log(`📱 WhatsApp message sent to ${patient.phone_number}`);
        } catch (error) {
          this.logger.error(`Failed to send WhatsApp message: ${error.message}`);
        }
      }

      return {
        success: true,
        message: `Successfully processed ${results.filter(r => r.success).length} daily workout records`,
        results,
        weeklyMessage
      };
    } catch (error) {
      this.logger.error(`Error processing file: ${error.message}`);
      throw new BadRequestException(`Failed to process file: ${error.message}`);
    }
  }
}
