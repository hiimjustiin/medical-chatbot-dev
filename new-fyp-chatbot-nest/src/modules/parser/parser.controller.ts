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
import { Logger } from '@nestjs/common';

@Controller('parser')
export class ParserController {
  private readonly logger = new Logger(ParserController.name);

  constructor(
    private readonly parserService: ParserService,
    private readonly supabaseService: SupabaseService,
  ) {}

  @Post('upload-workout')
  @UseInterceptors(FilesInterceptor('files', 1))
  async uploadWorkout(
    @UploadedFiles() files: Express.Multer.File[],
    @Body('patientId') patientId: string,
  ) {
    if (!files || files.length === 0) {
      throw new BadRequestException('No file uploaded');
    }

    if (!patientId) {
      throw new BadRequestException('Patient ID is required');
    }

    const file = files[0];
    const content = file.buffer.toString('utf-8');
    this.logger.log(`📄 Received file: ${file.originalname}`);

    try {
      // 解析运动数据
      const workoutData = await this.parserService.parseWorkoutData(content);
      this.logger.log(`📊 Parsed ${workoutData.length} workout records`);

      // 合并同一天的数据
      const grouped = this.parserService.groupWorkoutsByDay(workoutData);
      this.logger.log(`📅 Grouped into ${grouped.length} day(s)`);

      // 批量处理
      const results = await this.parserService.processWorkoutsBatch(grouped, patientId);

      return {
        success: true,
        message: `Successfully processed ${results.filter(r => r.success).length} daily workout records`,
        results
      };
    } catch (error) {
      this.logger.error(`Error processing file: ${error.message}`);
      throw new BadRequestException(`Failed to process file: ${error.message}`);
    }
  }
}
