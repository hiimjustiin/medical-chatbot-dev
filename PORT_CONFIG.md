# 端口配置说明

## 🚀 服务端口分配

| 服务 | 端口 | 说明 | 启动命令 |
|------|------|------|----------|
| **前端 (Next.js)** | 3001 | 患者管理界面 | `npm run dev -- -p 3001` |
| **后端 (NestJS)** | 3000 | API服务 + GPT服务 | `npm run start:dev` |
| **WhatsApp机器人** | 5000 | 消息接收和转发 | `python main.py` |
| **ngrok隧道** | 动态 | 公网访问隧道 | `ngrok http 5000` |

## 🔧 端口冲突解决方案

### 问题描述
- 前端默认端口3000与后端NestJS冲突
- WhatsApp机器人需要转发到后端GPT服务

### 解决方案
1. **前端使用端口3001**
2. **后端保持端口3000**
3. **WhatsApp机器人转发到端口3000**

## 📋 启动顺序

### 1️⃣ 启动后端服务
```bash
cd new-fyp-chatbot-nest
npm run start:dev
# 或双击 start-backend.bat
```

### 2️⃣ 启动前端服务 (新终端)
```bash
cd patient-tracker
npm run dev -- -p 3001
# 或双击 start-frontend.bat
```

### 3️⃣ 启动WhatsApp机器人 (新终端)
```bash
cd whatsapp-bot
python main.py
# 或双击 start-whatsapp.bat
```

### 4️⃣ 启动ngrok隧道 (新终端)
```bash
D:\Downloads\ngrok-v3-stable-windows-amd64\ngrok.exe http 5000
```

## 🌐 访问地址

- **前端界面**: http://localhost:3001
- **后端API**: http://localhost:3000
- **GPT服务**: http://localhost:3000/chat/message
- **WhatsApp Webhook**: http://localhost:5000/webhook
- **ngrok公网地址**: https://[ngrok-id].ngrok.io

## 🔄 消息流程

```
WhatsApp用户 → Meta API → ngrok → 端口5000 → 端口3000 → GPT API → 回复用户
```

## ⚠️ 注意事项

1. **端口顺序**: 必须先启动后端，再启动前端和机器人
2. **ngrok隧道**: 必须保持运行状态
3. **环境变量**: 确保.env文件配置正确
4. **服务依赖**: 前端依赖后端API，机器人依赖后端GPT服务

## 🚨 故障排除

### 端口被占用
```bash
# 查看端口占用
netstat -ano | findstr :3000
netstat -ano | findstr :3001
netstat -ano | findstr :5000

# 结束进程
taskkill /PID [进程ID] /F
```

### 服务无法启动
1. 检查端口是否被占用
2. 确认依赖服务是否运行
3. 查看错误日志
4. 验证环境变量配置

## 📞 支持

如需帮助：
1. 检查端口配置
2. 确认启动顺序
3. 查看服务日志
4. 运行测试脚本
