import { Module } from '@nestjs/common';
import { ChatController } from './modules/gpt/gpt.controller';
import { ChatService } from './modules/gpt/gpt.service';
import { AppController } from './modules/app/app.controller';
import { ParserController } from './modules/parser/parser.controller';
import { ExerciseController } from './modules/exercise/exercise.controller';
import { MapController } from './modules/map/map.controller';
import { AppService } from './modules/app/app.service';
import { ParserService } from './modules/parser/parser.service';
import { SupabaseService } from './modules/supabase/supabase.service';
import { MapService } from './modules/map/map.service';
import { ExerciseService } from './modules/exercise/exercise.service';
import { PatientService } from './modules/patient/patient.service';
import { PatientController } from './modules/patient/patient.controller';
import { UserAvailabilityService } from './modules/userAvailability/user_availability.service';
import { ExerciseAllocationService } from './modules/exercise/exercise_allocation.service';
import { ExerciseSummaryService } from './modules/exercise/exercise_summary.service';

import { ConfigModule } from '@nestjs/config';
import { RedisModule } from './modules/redis/redis.module';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true, // Makes the config available globally
    }),
    RedisModule,
  ],
  controllers: [
    ChatController,
    AppController,
    ParserController,
    ExerciseController,
    MapController,
    PatientController,
  ],
  providers: [
    ChatService,
    AppService,
    ParserService,
    SupabaseService,
    MapService,
    ExerciseService,
    PatientService,
    UserAvailabilityService,
    ExerciseAllocationService,
    ExerciseSummaryService,
  ],
})
export class AppModule {}
