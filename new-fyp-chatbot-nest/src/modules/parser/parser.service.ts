import { Injectable, Logger } from '@nestjs/common';
import { SupabaseService } from '../supabase/supabase.service';

interface HeartRateData {
  date: string;
  heartrate: number;
}

interface WorkoutData {
  userID: string;
  startDate: string;
  duration: number;
  steps: number;
  distance: number;
  calories: number;
  moderateIntensity: number;
  vigorousIntensity: number;
  heartrate: HeartRateData[];
}

@Injectable()
export class ParserService {
  private readonly logger = new Logger(ParserService.name);

  constructor(private readonly supabaseService: SupabaseService) {}

  async parseWorkoutData(fileContent: string): Promise<WorkoutData[]> {
    const lines = fileContent.trim().split('\n');
    const results: WorkoutData[] = [];

    if (lines.length <= 1) {
      this.logger.warn('TXT 文件中没有有效的数据行');
      return results;
    }

    // 跳过表头
    for (let i = 1; i < lines.length; i++) {
      const line = lines[i];
      if (!line.trim()) continue;

      const [
        userID,
        startDate,
        duration,
        steps,
        distance,
        calories,
        moderateIntensity,
        vigorousIntensity,
        heartrateJson
      ] = line.split(';');

      try {
        const heartrate = heartrateJson ? JSON.parse(heartrateJson) : [];
        
        results.push({
          userID,
          startDate,
          duration: parseInt(duration),
          steps: parseInt(steps),
          distance: parseFloat(distance),
          calories: parseFloat(calories),
          moderateIntensity: parseInt(moderateIntensity),
          vigorousIntensity: parseInt(vigorousIntensity),
          heartrate
        });
      } catch (error) {
        this.logger.error(`解析第 ${i + 1} 行时出错: ${error.message}`);
      }
    }

    return results;
  }

  async calculateExerciseDuration(heartrate: HeartRateData[]): Promise<number> {
    if (!heartrate || heartrate.length === 0) return 0;

    let duration = 0;
    let startTime: string | null = null;
    const threshold = 100; // 固定心率为 100

    for (let i = 0; i < heartrate.length; i++) {
      const current = heartrate[i];
      
      if (current.heartrate > threshold) {
        if (!startTime) {
          startTime = current.date;
        }
      } else if (startTime) {
        const start = new Date(startTime);
        const end = new Date(current.date);
        duration += (end.getTime() - start.getTime()) / 1000; // 转换为秒
        startTime = null;
      }
    }

    // 处理最后一个时间段
    if (startTime) {
      const start = new Date(startTime);
      const end = new Date(heartrate[heartrate.length - 1].date);
      duration += (end.getTime() - start.getTime()) / 1000;
    }

    return Math.round(duration / 60); // 转换为分钟并四舍五入
  }

  // 新增：按天合并运动数据
  groupWorkoutsByDay(records: WorkoutData[]): WorkoutData[] {
    const grouped: { [date: string]: WorkoutData } = {};
    for (const rec of records) {
      // 只取日期部分
      const day = rec.startDate.split('T')[0];
      if (!grouped[day]) {
        grouped[day] = {
          ...rec,
          startDate: day,
          heartrate: Array.isArray(rec.heartrate) ? [...rec.heartrate] : [],
        };
      } else {
        grouped[day].duration += rec.duration;
        grouped[day].steps += rec.steps;
        grouped[day].distance += rec.distance;
        grouped[day].calories += rec.calories;
        grouped[day].moderateIntensity += rec.moderateIntensity;
        grouped[day].vigorousIntensity += rec.vigorousIntensity;
        grouped[day].heartrate = grouped[day].heartrate.concat(rec.heartrate || []);
      }
    }
    return Object.values(grouped);
  }

  // 批量处理并入库
  async processWorkoutsBatch(workoutList: WorkoutData[], patientId: string) {
    try {
      // 获取患者信息（仅用于验证患者存在）
      const patient = await this.supabaseService.getPatientById(patientId);
      if (!patient) {
        throw new Error(`Patient not found: ${patientId}`);
      }
      const results = [];
      for (const workoutData of workoutList) {
        // 计算超过 100 心率的时间
        const exerciseDuration = await this.calculateExerciseDuration(workoutData.heartrate);
        
        // 保存到数据库
        await this.supabaseService.insertWorkoutData({
          patient_id: patientId,
          start_date: workoutData.startDate,
          duration: workoutData.duration,
          steps: workoutData.steps,
          distance: workoutData.distance,
          calories: workoutData.calories,
          moderate_intensity: exerciseDuration, // 使用相同的时间
          vigorous_intensity: exerciseDuration, // 使用相同的时间
          heartrate_data: workoutData.heartrate
        });
        results.push({
          date: workoutData.startDate,
          success: true,
          exerciseDuration
        });
      }
      return results;
    } catch (error) {
      this.logger.error(`Batch process error: ${error.message}`);
      throw error;
    }
  }
}
