# AI个性化回复系统 - 具体操作指南

## 🎯 快速开始：立即实施的步骤

### 第一步：配置GPT集成

**1. 获取OpenAI API密钥**
- 访问 https://platform.openai.com/api-keys
- 创建新的API密钥
- 复制密钥备用

**2. 配置后端环境变量**
在 `new-fyp-chatbot-nest/.env` 文件中添加：
```env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.7
```

**3. 测试GPT连接**
```bash
cd new-fyp-chatbot-nest
npm run start:dev
# 访问 http://localhost:3000/api/gpt/test
```

### 第二步：实现基础个性化回复

**1. 修改患者服务** (`new-fyp-chatbot-nest/src/modules/patient/patient.service.ts`)
```typescript
async getPatientContext(patientId: string) {
  const patient = await this.getPatientById(patientId);
  const exercises = await this.getRecentExercises(patientId);
  const healthData = await this.getHealthMetrics(patientId);
  
  return {
    patientInfo: patient,
    recentActivity: exercises,
    healthStatus: healthData,
    lastInteraction: await this.getLastMessage(patientId)
  };
}
```

**2. 创建个性化回复生成器** (`new-fyp-chatbot-nest/src/modules/gpt/personalized-generator.ts`)
```typescript
export class PersonalizedResponseGenerator {
  async generateResponse(patientId: string, userMessage: string): Promise<string> {
    const context = await this.patientService.getPatientContext(patientId);
    
    const prompt = this.buildPrompt(context, userMessage);
    const response = await this.openaiService.generateCompletion(prompt);
    
    return this.formatResponse(response);
  }
  
  private buildPrompt(context: any, userMessage: string): string {
    return `
你是一个专业的医疗健康助手。基于以下患者信息生成个性化回复：

患者信息：
- 姓名：${context.patientInfo.name}
- 年龄：${context.patientInfo.age}
- 健康状况：${context.patientInfo.condition}

最近活动：
${context.recentActivity.map(act => `- ${act.type}: ${act.duration}分钟`).join('\n')}

健康数据：
${Object.entries(context.healthStatus).map(([k, v]) => `- ${k}: ${v}`).join('\n')}

用户问题：${userMessage}

请用温暖、专业的语气回复，提供具体可行的建议。
    `;
  }
}
```

### 第三步：集成到现有系统

**1. 修改GPT控制器** (`new-fyp-chatbot-nest/src/modules/gpt/gpt.controller.ts`)
```typescript
@Post('personalized/:patientId')
async getPersonalizedResponse(
  @Param('patientId') patientId: string,
  @Body() body: { message: string }
) {
  const generator = new PersonalizedResponseGenerator();
  return await generator.generateResponse(patientId, body.message);
}
```

**2. 前端调用示例** (`patient-tracker/app/dashboard/patients/_components/ChatInterface.tsx`)
```typescript
const sendMessage = async (patientId: string, message: string) => {
  const response = await fetch(`/api/gpt/personalized/${patientId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  });
  return await response.json();
};
```

## 🔧 具体配置参数

### 个性化程度调节
在 `config.py` 或环境变量中设置：
```python
PERSONALIZATION_CONFIG = {
    'use_demographic_data': True,      # 使用人口统计数据
    'use_behavioral_patterns': True,   # 使用行为模式
    'use_emotional_analysis': True,    # 情感分析
    'response_length': 'medium',       # short/medium/long
    'tone_adjustment': True,           # 语气调整
    'cultural_adaptation': True        # 文化适应
}
```

### 回复模板定制
创建回复模板文件 `response-templates.json`:
```json
{
  "encouraging": [
    "看到您坚持了{天数}天，这真的很棒！",
    "您已经完成了{完成率}%的计划，继续加油！"
  ],
  "educational": [
    "关于{健康话题}，研究表明：{事实}",
    "基于您的{健康状况}，建议关注：{建议}"
  ],
  "empathetic": [
    "我能理解您现在的感受，健康管理确实不容易",
    "每个人都会有起伏，重要的是不放弃"
  ]
}
```

## 📊 数据收集和处理

### 必需的患者数据字段
确保数据库包含以下字段：
```sql
-- patients表需要包含
age INT,
condition VARCHAR(255),
goals TEXT,
preferences JSON,
communication_style VARCHAR(50)

-- exercises表
completion_rate DECIMAL(5,2),
consistency_score INT,
preferred_times JSON

-- messages表
sentiment_score DECIMAL(3,2),
engagement_level INT,
response_time INT
```

### 实时数据更新
在WhatsApp机器人中添加数据收集：
```python
# whatsapp-bot/routes/webhook.py
async def handle_message(patient_id, message):
    # 记录消息情感
    sentiment = analyze_sentiment(message)
    
    # 更新患者互动数据
    update_patient_engagement(patient_id, sentiment)
    
    # 生成个性化回复
    personalized_response = generate_personalized_reply(patient_id, message)
    
    return personalized_response
```

## 🚀 部署到AWS使用Termius

### 第一步：AWS EC2实例准备

**1. 创建EC2实例**
- 选择Ubuntu 22.04 LTS
- 实例类型：t3.medium（推荐）
- 存储：至少20GB
- 安全组：开放端口22, 80, 443, 3000, 3001, 5000

**2. 配置Termius连接**
- 下载Termius应用
- 添加新主机：
  - 地址：你的EC2公有IP
  - 用户名：ubuntu
  - 认证：使用.pem密钥文件

### 第二步：服务器环境设置

通过Termius连接到服务器后执行：

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 安装Python
sudo apt install python3-pip -y

# 安装PM2（进程管理）
sudo npm install -g pm2

# 安装Nginx
sudo apt install nginx -y
```

### 第三步：部署应用程序

**1. 克隆代码到服务器**
```bash
cd /home/ubuntu
git clone https://github.com/your-username/medical-chatbot-system.git
cd medical-chatbot-system
```

**2. 部署后端服务**
```bash
cd new-fyp-chatbot-nest
npm install
npm run build

# 使用PM2启动
pm2 start npm --name "medical-backend" -- run start:prod
pm2 save
pm2 startup
```

**3. 部署前端服务**
```bash
cd ../patient-tracker
npm install
npm run build

# 使用PM2启动
pm2 start npm --name "medical-frontend" -- run start
pm2 save
```

**4. 部署WhatsApp机器人**
```bash
cd ../whatsapp-bot
pip3 install -r requirements.txt

# 使用PM2启动
pm2 start python3 --name "whatsapp-bot" -- main.py
pm2 save
```

### 第四步：Nginx反向代理配置

创建Nginx配置文件：
```bash
sudo nano /etc/nginx/sites-available/medical-chatbot
```

添加以下配置：
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端服务
    location / {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # 后端API
    location /api {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # WhatsApp webhook
    location /webhook {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

启用配置：
```bash
sudo ln -s /etc/nginx/sites-available/medical-chatbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 第五步：SSL证书配置

使用Let's Encrypt获取免费SSL证书：
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

### 第六步：环境变量配置

在服务器上创建环境变量文件：
```bash
# 后端环境变量
sudo nano /home/ubuntu/medical-chatbot-system/new-fyp-chatbot-nest/.env

# 添加以下内容
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
OPENAI_API_KEY=your_openai_key
NODE_ENV=production
PORT=3000

# WhatsApp机器人环境变量
sudo nano /home/ubuntu/medical-chatbot-system/whatsapp-bot/.env

# 添加以下内容
META_ACCESS_TOKEN=your_meta_token
META_PHONE_NUMBER_ID=your_phone_id
WEBHOOK_VERIFY_TOKEN=your_verify_token
```

### 第七步：监控和维护

**1. 设置自动重启**
```bash
# 确保PM2在系统重启后自动启动
pm2 startup
sudo env PATH=$PATH:/usr/bin /usr/lib/node_modules/pm2/bin/pm2 startup systemd -u ubuntu --hp /home/ubuntu
```

**2. 监控服务状态**
```bash
# 查看所有服务状态
pm2 status

# 查看日志
pm2 logs medical-backend
pm2 logs medical-frontend
pm2 logs whatsapp-bot
```

**3. 设置日志轮转**
```bash
sudo nano /etc/logrotate.d/medical-chatbot

# 添加以下内容
/home/ubuntu/.pm2/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
```

## 🔧 故障排除指南

### 常见问题解决

**1. 服务无法启动**
```bash
# 检查端口占用
sudo netstat -tulpn | grep :3000

# 检查日志
pm2 logs service-name

# 重启服务
pm2 restart service-name
```

**2. 数据库连接问题**
- 检查Supabase连接配置
- 验证网络连接
- 检查防火墙设置

**3. WhatsApp webhook验证失败**
- 检查verify token匹配
- 验证URL可访问性
- 检查Meta App配置

### 性能优化建议

**1. 数据库优化**
```sql
-- 为常用查询添加索引
CREATE INDEX idx_patient_exercises ON exercises(patient_id, date);
CREATE INDEX idx_message_sentiment ON messages(patient_id, sentiment_score);
```

**2. 缓存策略**
```typescript
// 实现患者数据缓存
const patientCache = new Map();

async function getCachedPatientData(patientId: string) {
  if (patientCache.has(patientId)) {
    return patientCache.get(patientId);
  }
  
  const data = await fetchPatientData(patientId);
  patientCache.set(patientId, data);
  
  // 5分钟缓存
  setTimeout(() => patientCache.delete(patientId), 300000);
  
  return data;
}
```

## 📞 技术支持

遇到问题时：
1. 首先检查PM2日志：`pm2 logs`
2. 查看Nginx错误日志：`sudo tail -f /var/log/nginx/error.log`
3. 检查系统资源：`htop` 或 `df -h`
4. 联系技术支持提供具体错误信息

---

**重要提示**：部署前请确保所有敏感信息（API密钥、数据库密码等）已正确配置，并进行充分测试。