import { config } from 'dotenv';
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import * as cors from 'cors';
import * as bodyParser from 'body-parser';  // ✅ 加入

config();

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  app.use(cors());

  // ✅ 添加这两行：支持 Twilio 的 x-www-form-urlencoded 请求体格式
  app.use(bodyParser.urlencoded({ extended: true }));
  app.use(bodyParser.json());

  const port = process.env.PORT || 3000 || 3001;
  await app.listen(port);
  console.log(`Application is running on: http://localhost:${port}`);
}
bootstrap();
