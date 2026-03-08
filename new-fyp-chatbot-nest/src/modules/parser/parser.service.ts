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
    const lines = fileContent.trim().split(/\r?\n/);
    const results: WorkoutData[] = [];

    if (lines.length === 0) {
      this.logger.warn('文件内容为空');
      return results;
    }

    const header = lines[0].trim();

    // 格式1：TSV 心率明细（date\theartrate\tsubject_code）
    const isTSVHeartRate = /\bdate\b\s*\t\s*\bheartrate\b\s*\t\s*\bsubject_code\b/i.test(header);

    if (isTSVHeartRate) {
      // 将心率按天聚合为WorkoutData，其他数值字段用0占位（后续由统计服务计算）
      const byDay: Record<string, HeartRateData[]> = {};
      let subjectCode = '';
      for (let i = 1; i < lines.length; i++) {
        const line = lines[i];
        if (!line || !line.trim()) continue;
        const parts = line.split('\t');
        if (parts.length < 3) continue;
        const [dateStr, hrStr, subj] = parts;
        if (!subjectCode && subj) subjectCode = subj.trim();
        const hr = Number(hrStr);
        if (!isFinite(hr)) continue;
        const iso = dateStr.trim();
        // 仅保留有效ISO字符串
        if (!iso) continue;
        const day = iso.split('T')[0];
        if (!byDay[day]) byDay[day] = [];
        byDay[day].push({ date: iso, heartrate: hr });
      }

      Object.entries(byDay).forEach(([day, hrList]) => {
        // 保持时间顺序
        hrList.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
        results.push({
          userID: subjectCode || 'unknown',
          startDate: `${day}T00:00:00Z`,
          duration: 0,
          steps: 0,
          distance: 0,
          calories: 0,
          moderateIntensity: 0,
          vigorousIntensity: 0,
          heartrate: hrList,
        });
      });

      return results;
    }

    // 格式2：原有分号分隔记录行
    if (lines.length <= 1) {
      this.logger.warn('TXT 文件中没有有效的数据行');
      return results;
    }

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
        heartrateJson,
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
          heartrate,
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
      // patientId 可能是 subject_code 或实际的数据库 ID
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
