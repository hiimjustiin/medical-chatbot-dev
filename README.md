# Medical Chatbot System

A comprehensive medical health management platform featuring a patient tracking dashboard, a WhatsApp automated messaging system, and AI-driven personalized health recommendations.

## 🏗️ Project Architecture

This project adopts a microservices architecture consisting of three main components:

### 1. Backend Service (NestJS)
- **Location**: `new-fyp-chatbot-nest/`
- **Tech Stack**: NestJS, TypeScript, Supabase
- **Functions**: RESTful API, patient data management, exercise plan assignment, GPT integration

### 2. 前端仪表板 (Next.js)
- **Location**: `patient-tracker/`
- **Tech Stack**: Next.js 14, React, Tailwind CSS, Radix UI
- **Functions**: Patient management interface, data visualization, report uploading

### 3. WhatsApp Bot (Python)
- **Location**: `whatsapp-bot/`
- **Tech Stack**: Python, Flask, Meta WhatsApp API
- **Functions**: Automated message sending, health reminders, personalized communication.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.8+
- Supabase account
- Meta WhatsApp Business API access permissions

### Installation and Execution

#### 1. Backend Service
```bash
cd new-fyp-chatbot-nest
npm install
npm run start:dev
```

#### 2. Frontend Dashboard
```bash
cd patient-tracker
npm install
npm run dev
```

#### 3. WhatsApp Bot
```bash
cd whatsapp-bot
pip install -r requirements.txt
python main.py
```

## 📁 Project Structure

```
medical-chatbot-dev/
├── new-fyp-chatbot-nest/          # Backend API Service
│   ├── src/modules/
│   │   ├── app/                   # App Configuration
│   │   ├── exercise/              # Exercise Management
│   │   ├── gpt/                   # AI Integration
│   │   ├── patient/               # Patient Management
│   │   └── supabase/              # Database Services
│   └── package.json
├── patient-tracker/               # Frontend Dashboard
│   ├── app/                       # Next.js App Router
│   ├── components/                # UI Components
│   └── package.json
└── whatsapp-bot/                  # WhatsApp Bot
    ├── routes/                    # API Routes
    ├── config.py                  # Configuration Management
    └── requirements.txt
```

## 🔧 Configuration Instructions

### Environment Variables
Each subdirectory contains environment template files:
- `new-fyp-chatbot-nest/env_template.txt` - Backend env variables
- `patient-tracker/create_env.py` - Frontend env configuration
- `whatsapp-bot/create_env.py` - Bot env configuration

### Database Configuration
The project uses Supabase as the database backend. You need to configure:
- SUPABASE_URL
- SUPABASE_ANON_KEY
- Database table structure (refer to database.sql)

## 🤖 AI Personalized Response System

### Core Features
1. **Patient Profiling** - Build health profiles based on historical data
2. **Personalized Advice** - Provide customized health suggestions based on patient conditions
3. **Smart Reminders** - Intelligent reminder system based on behavior patterns
4. **Sentiment Analysis** - Analyze patient emotional states to adjust communication strategies

### Implementation Mechanism
- **GPT Integration**: AI dialogue implemented via the gpt module
- **Data-Driven**: Based on patient exercise data, health metrics, and historical interactions
- **Context-Awareness**: Maintains conversation context to provide a coherent experience.

## 📊 Data Model

### Main Tables
- `patients` - Basic patient information
- `exercises` - Exercise plan data
- `workouts` - Exercise records (logs)
- `messages` - Communication history
- `health_metrics` - Health indicators

### Data Relationships
Patient ↔ Exercise Plan ↔ Exercise Records ↔ Health Metrics ↔ Communication History

## 🔒 安全特性

- JWT身份验证
- 数据加密存储
- API访问控制
- 输入验证和清理

## 📈 监控和日志

- 应用性能监控
- 错误日志记录
- 用户行为分析
- 系统健康检查

## 🧪 测试

### 运行测试
```bash
# 后端测试
cd new-fyp-chatbot-nest
npm test

# 前端测试  
cd patient-tracker
npm test

# WhatsApp机器人测试
cd whatsapp-bot
python -m pytest
```

## 🚢 部署

### 生产环境部署
1. **后端**: 使用PM2或Docker部署
2. **前端**: Vercel或Netlify部署
3. **机器人**: 云服务器部署

### 环境配置
- 生产环境变量设置
- SSL证书配置
- 数据库备份策略
- 监控告警设置

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看LICENSE文件了解详情。

## 📞 支持

如有问题或建议，请通过以下方式联系：
- 创建Issue
- 发送邮件至项目维护者
- 查看文档获取更多信息

---

**注意**: 本项目涉及医疗健康数据，请确保遵守相关隐私法规和数据保护法律。
