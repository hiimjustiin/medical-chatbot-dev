import { config } from 'dotenv';
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import * as cors from 'cors';
import * as bodyParser from 'body-parser';
import * as fs from 'fs';  // 引入文件模块

config();

async function bootstrap() {
  // //  读取 HTTPS 证书
  // const httpsOptions = {
  //   key: fs.readFileSync('./cert.key'),
  //   cert: fs.readFileSync('./cert.pem'), 
  // };

  // 本地开发用 HTTP
  const app = await NestFactory.create(AppModule); // 不传 httpsOptions
  app.use(cors());

  app.use(bodyParser.urlencoded({ extended: true }));
  app.use(bodyParser.json());

  const port = process.env.PORT ?? 3005;
  await app.listen(port);
  console.log(`Application is running on: http://localhost:${port}`); // 改为 http
}
bootstrap();

