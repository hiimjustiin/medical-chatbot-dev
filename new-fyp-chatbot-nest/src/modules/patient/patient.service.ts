import { Injectable } from '@nestjs/common';
import { SupabaseService } from '../supabase/supabase.service';

@Injectable()
export class PatientService {
  constructor(private readonly supabaseService: SupabaseService) {}

  async getPatients() {
    try {
      const { data, error } = await this.supabaseService
        .getClient()
        .from('patients')
        .select('*')
        .order('full_name', { ascending: true });

      if (error) {
        throw new Error(
          `Error fetching patients: ${error.message}`,
        );
      }

      return data;
    } catch (error) {
      console.error('Error in getPatients', error);
      throw error;
    }
  }

  async addNewPatient(patientData: any) {
    try {
      // Insert into doctor_inputs table
      const { data, error: insertError } = await this.supabaseService
        .getClient()
        .from('patients')
        .insert([patientData])
        .select('id') // Retrieve the generated Id of the new row
        .single();

      if (insertError) {
        if (insertError.message.includes('duplicate key value')) {
          return {
            success: false,
            message: 'Patient already exists',
          };
        }

        throw new Error(
          `Error inserting into patients: ${insertError.message}`,
        );
      }

      // Get the patient ID from the new row
      const patientId = data?.id ?? null;

      return {
        success: true,
        message: 'Patient added successfully',
        patientId,
      };
    } catch (error) {
      throw new Error(`Failed to add new patient: ${error.message}`);
    }
  }

  async deletePatient(patientId: any) {
    try {
      // Delete from patients table
      const { error: patientsError } = await this.supabaseService
        .getClient()
        .from('patients')
        .delete()
        .eq('id', patientId);

      if (patientsError) {
        throw new Error(
          `Error deleting from table: ${patientsError.message}`,
        );
      }

      return { success: true, message: 'Patient deregistered successfully' };
    } catch (error) {
      throw new Error(`Failed to deregister patient: ${error.message}`);
    }
  }
}
