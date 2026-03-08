import { Controller, Get, Post, Body, Delete, HttpException, HttpStatus, Put } from '@nestjs/common';
import { PatientService } from './patient.service';

@Controller('api/data') // ✅ 保持原路径兼容
export class PatientController {
  constructor(private readonly patientService: PatientService) {}

  @Get('get-patients')
  async getAllPatients() {
    try {
      const patients = await this.patientService.getPatients();

      if (!patients || patients.length === 0) {
        return {
          statusCode: 204,
          message: 'No patient display data found',
          patients: [],
        };
      }

      return {
        statusCode: 200,
        message: 'Patient display data fetched successfully',
        patients,
      };
    } catch (error) {
      return {
        statusCode: 500,
        message: 'Error fetching patient data',
        error: error.message,
      };
    }
  }

  @Post('add-patient')
  async addPatient(@Body() patientData: any) {
    try {
      const result = await this.patientService.addNewPatient(patientData);

      if (!result.success) {
        throw new HttpException(result.message, HttpStatus.BAD_REQUEST);
      }

      return {
        success: true,
        message: 'Patient added successfully',
        patientId: result.patientId,
      };
    } catch (error) {
      throw new HttpException(error.message, HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }

  @Delete('delete-patient')
  async deletePatient(@Body('id') id: string) {
    try {
      const result = await this.patientService.deletePatient(id);

      if (!result.success) {
        throw new HttpException(result.message, HttpStatus.BAD_REQUEST);
      }

      return {
        success: true,
        message: 'Patient deleted successfully',
      };
    } catch (error) {
      throw new HttpException(error.message, HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }

  @Put('update-patient')
  async updatePatient(@Body('id') id: string, @Body('updates') updates: any) {
    try {
      if (!id || !updates || typeof updates !== 'object') {
        throw new HttpException('Invalid payload', HttpStatus.BAD_REQUEST);
      }
      const result = await this.patientService.updatePatient(id, updates);
      return { success: true, patient: result.patient };
    } catch (error) {
      throw new HttpException(error.message, HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }
}

