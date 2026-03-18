# 医疗聊天机器人系统 (Medical Chatbot System)

一个完整的医疗健康管理平台，包含患者追踪仪表板、WhatsApp自动消息系统和AI驱动的个性化健康建议。

## 🏗️ 项目架构

本项目采用微服务架构，包含三个主要组件：

### 1. 后端服务 (NestJS)
- **位置**: `new-fyp-chatbot-nest/`
- **技术栈**: NestJS, TypeScript, Supabase
- **功能**: RESTful API, 患者数据管理, 运动计划分配, GPT集成

### 2. 前端仪表板 (Next.js)
- **位置**: `patient-tracker/`
- **技术栈**: Next.js 14, React, Tailwind CSS, Radix UI
- **功能**: 患者管理界面, 数据可视化, 报告上传

### 3. WhatsApp机器人 (Python)
- **位置**: `whatsapp-bot/`
- **技术栈**: Python, Flask, Meta WhatsApp API
- **功能**: 自动消息发送, 健康提醒, 个性化沟通

## 🚀 快速开始

### 环境要求
- Node.js 18+
- Python 3.8+
- Supabase账户
- Meta WhatsApp Business API访问权限

### 安装和运行

#### 1. 后端服务
```bash
cd new-fyp-chatbot-nest
npm install
npm run start:dev
```

#### 2. 前端仪表板
```bash
cd patient-tracker
npm install
npm run dev
```

#### 3. WhatsApp机器人
```bash
cd whatsapp-bot
pip install -r requirements.txt
python main.py
```

## 📁 项目结构

```
medical-chatbot-dev/
├── new-fyp-chatbot-nest/          # 后端API服务
│   ├── src/modules/
│   │   ├── app/                   # 应用配置
│   │   ├── exercise/              # 运动管理
│   │   ├── gpt/                   # AI集成
│   │   ├── patient/               # 患者管理
│   │   └── supabase/              # 数据库服务
│   └── package.json
├── patient-tracker/               # 前端仪表板
│   ├── app/                       # Next.js App Router
│   ├── components/                # UI组件
│   └── package.json
└── whatsapp-bot/                  # WhatsApp机器人
    ├── routes/                    # API路由
    ├── config.py                  # 配置管理
    └── requirements.txt
```

## 🔧 配置说明

### 环境变量配置
每个子目录都包含环境模板文件：
- `new-fyp-chatbot-nest/env_template.txt` - 后端环境变量
- `patient-tracker/create_env.py` - 前端环境配置
- `whatsapp-bot/create_env.py` - 机器人环境配置

### 数据库配置
项目使用Supabase作为数据库后端，需要配置以下信息：
- SUPABASE_URL
- SUPABASE_ANON_KEY
- 数据库表结构（参考database.sql）

## 🤖 AI个性化回复系统

### 核心功能
1. **患者画像分析** - 基于历史数据构建患者健康档案
2. **个性化建议** - 根据患者状况提供定制化健康建议
3. **智能提醒** - 基于行为模式的智能提醒系统
4. **情感分析** - 分析患者情绪状态调整沟通策略

### 实现机制
- **GPT集成**: 通过gpt模块实现AI对话
- **数据驱动**: 基于患者运动数据、健康指标和历史互动
- **上下文感知**: 维护对话上下文提供连贯体验

## 📊 数据模型

### 主要数据表
- `patients` - 患者基本信息
- `exercises` - 运动计划数据
- `workouts` - 运动记录
- `messages` - 沟通历史
- `health_metrics` - 健康指标

### 数据关系
患者 ↔ 运动计划 ↔ 运动记录 ↔ 健康指标 ↔ 沟通历史

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
