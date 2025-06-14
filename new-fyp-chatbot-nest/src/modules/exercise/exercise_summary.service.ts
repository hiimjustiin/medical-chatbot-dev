import { Injectable } from '@nestjs/common';
import { SupabaseService } from '../supabase/supabase.service';
import { DateTime } from 'luxon';

interface WeeklyReport {
  totalExerciseDuration: number;
  avgHeartRate: number;
  exerciseCount: number;
  totalModerateIntensity: number;
  totalVigorousIntensity: number;
  weeklyProgress: number;
}

@Injectable()
export class ExerciseSummaryService {
  constructor(private readonly supabaseService: SupabaseService) {}

  async getWeeklyReport(
    profileId: string,
    startOfWeek: string,
    endOfWeek: string,
  ): Promise<WeeklyReport> {
    const supabase = this.supabaseService.getClient();

    const patient = await this.supabaseService.getPatientById(profileId);
    if (!patient) {
      throw new Error(`未找到患者 ID: ${profileId}`);
    }

    const { data, error } = await supabase
      .from('workouts')
      .select('*')
      .eq('patient_id', profileId)
      .gte('start_date', startOfWeek)
      .lte('start_date', endOfWeek);

    if (error) {
      throw new Error(`获取运动数据失败: ${error.message}`);
    }

    if (!data || data.length === 0) {
      return {
        totalExerciseDuration: 0,
        avgHeartRate: 0,
        exerciseCount: 0,
        totalModerateIntensity: 0,
        totalVigorousIntensity: 0,
        weeklyProgress: 0
      };
    }

    const totalExerciseDuration = data.reduce(
      (sum, session) => sum + (session.moderate_intensity + session.vigorous_intensity),
      0
    );

    let totalHeartRateSum = 0;
    let totalHeartRateCount = 0;
    data.forEach((session) => {
      if (session.heartrate_data && Array.isArray(session.heartrate_data)) {
        session.heartrate_data.forEach((hr) => {
          if (hr.heartrate) {
            totalHeartRateSum += hr.heartrate;
            totalHeartRateCount++;
          }
        });
      }
    });
    const avgHeartRate = totalHeartRateCount > 0 ? totalHeartRateSum / totalHeartRateCount : 0;

    const weeklyProgress = patient.target_duration_week > 0
      ? Math.min(100, (totalExerciseDuration / patient.target_duration_week) * 100)
      : 0;

    return {
      totalExerciseDuration,
      avgHeartRate,
      exerciseCount: data.length,
      totalModerateIntensity: data.reduce((sum, session) => sum + session.moderate_intensity, 0),
      totalVigorousIntensity: data.reduce((sum, session) => sum + session.vigorous_intensity, 0),
      weeklyProgress
    };
  }

  async getWeeklyProgressMessage(profileId: string): Promise<string> {
    const now = DateTime.now();
    const startOfWeek = now.startOf('week').toISO();
    const endOfWeek = now.endOf('week').toISO();

    const report = await this.getWeeklyReport(profileId, startOfWeek, endOfWeek);
    const patient = await this.supabaseService.getPatientById(profileId);

    if (!patient) {
      throw new Error(`未找到患者 ID: ${profileId}`);
    }

    const remainingMinutes = Math.max(0, patient.target_duration_week - report.totalExerciseDuration);
    const progressPercentage = Math.round(report.weeklyProgress);

    let message = `本周运动进度报告 (${now.startOf('week').toFormat('MM-dd')} 至 ${now.endOf('week').toFormat('MM-dd')}):\n\n`;
    message += `总运动时间: ${report.totalExerciseDuration} 分钟\n`;
    message += `目标完成度: ${progressPercentage}%\n`;
    message += `平均心率: ${report.avgHeartRate.toFixed(1)} bpm\n`;
    message += `运动次数: ${report.exerciseCount} 次\n`;
    message += `中等强度运动: ${report.totalModerateIntensity} 分钟\n`;
    message += `高强度运动: ${report.totalVigorousIntensity} 分钟\n\n`;

    if (remainingMinutes > 0) {
      message += `距离本周目标还差 ${remainingMinutes} 分钟，请继续加油！`;
    } else {
      message += `恭喜您已完成本周运动目标！`;
    }

    return message;
  }
}
