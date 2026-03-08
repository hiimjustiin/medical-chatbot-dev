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
      throw new Error(`Patient not found with ID: ${profileId}`);
    }

    const { data, error } = await supabase
      .from('workouts')
      .select('*')
      .eq('patient_id', profileId)
      .gte('start_date', startOfWeek)
      .lte('start_date', endOfWeek);

    if (error) {
      throw new Error(`Failed to get workout data: ${error.message}`);
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
      throw new Error(`Patient not found with ID: ${profileId}`);
    }

    const remainingMinutes = Math.max(0, patient.target_duration_week - report.totalExerciseDuration);
    const progressPercentage = Math.round(report.weeklyProgress);

    let message = `Weekly exercise progress report (${now.startOf('week').toFormat('MM-dd')} to ${now.endOf('week').toFormat('MM-dd')}):\n\n`;
    message += `Total exercise duration: ${report.totalExerciseDuration} minutes\n`;
    message += `Target completion: ${progressPercentage}%\n`;
    message += `Average heart rate: ${report.avgHeartRate.toFixed(1)} bpm\n`;
    message += `Number of workouts: ${report.exerciseCount}\n`;
    message += `Moderate intensity exercise: ${report.totalModerateIntensity} minutes\n`;
    message += `Vigorous intensity exercise: ${report.totalVigorousIntensity} minutes\n\n`;

    if (remainingMinutes > 0) {
      message += `You still need ${remainingMinutes} minutes to reach your weekly goal. Keep going!`;
    } else {
      message += `Congratulations! You have completed your weekly exercise goal.`;
    }

    return message;
  }
}