import {
  Body,
  Controller,
  HttpException,
  HttpStatus,
  Post,
  Get,
  Delete,
} from '@nestjs/common';
import { SupabaseService } from '../supabase/supabase.service';
import { PatientService } from '../patient/patient.service';

@Controller('api/data')
export class AppController {
  constructor(
    private readonly supabaseService: SupabaseService,
    private readonly patientService: PatientService,
  ) {}

  @Post('get-profile-id')
  async getProfileId(@Body('fullName') fullName: string) {
    if (!fullName) {
      throw new HttpException('Full name is required', HttpStatus.BAD_REQUEST);
    }

    const { id, error } =
      await this.supabaseService.getProfileIdByName(fullName);

    if (error) {
      // Throw an HttpException with the specific error message
      throw new HttpException(error, HttpStatus.BAD_REQUEST);
    }

    return { profileId: id };
  }
  
  @Get('get-patient-names')
  async getPatientNames() {
    try {
      const patients = await this.supabaseService.getPatientNames();

      if (!patients || patients.length === 0) {
        throw new HttpException('No patients found', HttpStatus.NOT_FOUND);
      }

      return { patients };
    } catch (error) {
      throw new HttpException(
        error.message || 'An error occurred while fetching patient names',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }
}
