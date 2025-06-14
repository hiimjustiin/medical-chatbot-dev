import { Injectable, Logger } from '@nestjs/common';

@Injectable()
export class ParserService {
  private readonly logger = new Logger(ParserService.name);

  async extractMultiplePatientsFromTxt(fileContent: string): Promise<
    Array<{
      phone: string;
      patient: {
        name: string;
        age: number;
        condition: string;
        appointment: string;
        doctor: string;
      };
    }>
  > {
    const lines = fileContent.trim().split('\n');

    if (lines.length <= 1) {
      this.logger.warn('TXT 文件中没有有效的数据行');
      return [];
    }

    const header = lines[0];
    this.logger.log(`读取到表头: ${header}`);

    const results = [];

    for (let i = 1; i < lines.length; i++) {
      const line = lines[i];
      if (!line.trim()) continue; // 跳过空行

      const [
        userID,
        phoneNumber,
        startDate,
        duration,
        steps,
        distance,
        calories,
        moderate,
        vigorous,
        heartrateJson
      ] = line.split(';');

      if (!phoneNumber || !startDate) {
        this.logger.warn(`第 ${i + 1} 行缺少手机号或起始日期，跳过`);
        continue;
      }

      const patient = {
        name: `User ${userID}`,
        age: 60, // 默认年龄，你也可以根据用户数据填充
        condition: 'Your recent fitness activity',
        appointment: new Date(startDate).toISOString().split('T')[0],
        doctor: 'Dr. AI Health Bot',
      };

      const phone = phoneNumber.startsWith('+')
        ? phoneNumber.trim()
        : `+65${phoneNumber.trim()}`;

      this.logger.log(`第 ${i + 1} 行解析成功，phone=${phone}`);

      results.push({ phone, patient });
    }

    this.logger.log(`总共成功解析 ${results.length} 条患者信息`);
    return results;
  }
}
