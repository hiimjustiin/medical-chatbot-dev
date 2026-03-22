import { Injectable } from '@nestjs/common';
import { SupabaseService } from '../supabase/supabase.service';

@Injectable()
export class ExerciseService {
  constructor(private readonly supabaseService: SupabaseService) {}

  async getRandomExercise() {
    const { data, error } = await this.supabaseService
      .getClient()
      .from('exercises')
      .select('*'); // Fetch all exercises

    if (error) {
      console.error('Error fetching exercises:', error.message);
      throw new Error(`Error fetching exercises: ${error.message}`);
    }

    if (data && data.length > 0) {
      // Randomly select one exercise
      const randomIndex = Math.floor(Math.random() * data.length);
      return data[randomIndex];
    }

    throw new Error('No exercises found');
  }

  async checkInactivity(patientId: string) {
    const client = this.supabaseService.getClient();

    // 1. Get the most recent workout for this patient
    const { data, error } = await client
      .from('workouts')
      .select('start_date')
      .eq('patient_id', patientId)
      .order('start_date', { ascending: false })
      .limit(1)
      .single();

    if (error && error.code !== 'PGRST116') { // PGRST116 means "no rows found"
      throw new Error(`Error checking inactivity: ${error.message}`);
    }

    // 2. Logic: If no workout exists OR if the last one was > 2 days ago
    const lastWorkoutDate = data ? new Date(data.start_date) : null;
    const today = new Date();

    // Calculate difference in days
    const diffTime = lastWorkoutDate ? Math.abs(today.getTime() - lastWorkoutDate.getTime()) : Infinity;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (!lastWorkoutDate || diffDays >= 2) {
      return { shouldPrompt: true, daysInactive: diffDays };
    }

    return { shouldPrompt: false, daysInactive: diffDays };
  }

  async checkHeartRateIntensity(patientId: string) {
    const client = this.supabaseService.getClient();

    try {
      // 1. Fetch Patient
      const { data: patient, error: pError } = await client
        .from('patients')
        .select('moderate_hr_min')
        .eq('id', patientId)
        .maybeSingle();

      if (pError) throw new Error(`Patient Fetch Error: ${pError.message}`);
      if (!patient) return { status: 'error', message: `No patient found with ID: ${patientId}` };

      // 2. Fetch Latest Workout
      const { data: workout, error: wError } = await client
        .from('workouts')
        .select('heartrate_data')
        .eq('patient_id', patientId)
        .order('created_at', { ascending: false })
        .limit(1)
        .maybeSingle();

      if (wError) throw new Error(`Workout Fetch Error: ${wError.message}`);
      if (!workout) return { status: 'error', message: 'No workout found for this patient.' };

      // 3. Process Heart Rate Data
      let hrList = workout.heartrate_data;

      // Ensure hrList is an array (Handle cases where it's a single number or string)
      if (typeof hrList === 'number') hrList = [hrList];
      if (typeof hrList === 'string') hrList = JSON.parse(hrList);
      if (!Array.isArray(hrList)) throw new Error('heartrate_data is not an array format. Use [120, 130]');

      // 4. Calculate Average
      const sum = hrList.reduce((acc: number, val: any) => acc + Number(val), 0);
      const avgHR = sum / hrList.length;
      const target = patient.moderate_hr_min || 120;

      return {
        success: true,
        averageHR: avgHR.toFixed(1),
        targetHR: target,
        isLow: avgHR < target,
        message: avgHR < target ? "Push harder!" : "Goal reached!"
      };

    } catch (err: any) {
      // This sends the REAL error to your browser instead of "Internal Server Error"
      return { 
        success: false, 
        error_type: 'Code Crash',
        details: err.message 
      };
    }
  }
}
