# 部署指南和GitHub上传说明

## 📋 项目状态检查

在部署前，请确认项目已清理完成：

### ✅ 已完成的清理工作
- [x] 删除不必要的测试文件（20+个workout文件）
- [x] 移除调试脚本和临时文件（50+个文件）
- [x] 清理冗余文档文件
- [x] 修复重复的配置文件
- [x] 创建完整的.gitignore文件
- [x] 编写详细的项目文档

### 🔍 当前项目结构
```
medical-chatbot-dev/
├── new-fyp-chatbot-nest/     # 后端服务（已清理）
├── patient-tracker/          # 前端仪表板（已清理）
├── whatsapp-bot/            # WhatsApp机器人（已清理）
├── README.md               # 主项目文档
├── AI_GUIDANCE.md          # AI个性化回复指导
├── .gitignore             # Git忽略规则
└── DEPLOYMENT_GUIDE.md    # 本文件
```

## 🚀 GitHub上传步骤

### 步骤1: 创建GitHub仓库
1. 登录GitHub账户
2. 点击"New repository"
3. 输入仓库名称: `medical-chatbot-system`
4. 描述: "完整的医疗健康管理平台，包含患者追踪、AI个性化回复和WhatsApp自动化"
5. 选择公开或私有
6. 不初始化README（我们已有）

### 步骤2: 配置远程仓库
```bash
# 在项目根目录执行
git remote add origin https://github.com/your-username/medical-chatbot-system.git
```

### 步骤3: 推送代码
```bash
# 首次推送
git push -u origin main

# 后续推送
git push origin main
```

## 🔧 环境配置

### 后端服务配置
1. 复制环境模板：
```bash
cd new-fyp-chatbot-nest
cp env_template.txt .env
```

2. 配置必要的环境变量：
```env
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
OPENAI_API_KEY=your_openai_key
PORT=3000
```

### 前端配置
1. 运行环境设置脚本：
```bash
cd patient-tracker
python create_env.py
```

2. 配置Supabase连接

### WhatsApp机器人配置
1. 设置环境变量：
```bash
cd whatsapp-bot
python create_env.py
```

2. 配置Meta WhatsApp API凭证

## 🐳 Docker部署（可选）

### Dockerfile示例（后端）
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "run", "start:prod"]
```

### docker-compose.yml
```yaml
version: '3.8'
services:
  backend:
    build: ./new-fyp-chatbot-nest
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    
  frontend:
    build: ./patient-tracker
    ports:
      - "3001:3001"
    depends_on:
      - backend
    
  whatsapp-bot:
    build: ./whatsapp-bot
    ports:
      - "5000:5000"
```

## ☁️ 云平台部署

### Vercel（前端）
1. 连接GitHub仓库到Vercel
2. 配置环境变量
3. 自动部署

### Railway/Heroku（后端）
1. 连接代码仓库
2. 设置构建命令：`npm run build`
3. 配置启动命令：`npm run start:prod`
4. 设置环境变量

### 云服务器部署
```bash
# 服务器初始化
sudo apt update && sudo apt upgrade -y
sudo apt install nodejs npm python3-pip nginx -y

# 克隆代码
git clone https://github.com/your-username/medical-chatbot-system.git
cd medical-chatbot-system

# 安装依赖
cd new-fyp-chatbot-nest && npm install
cd ../patient-tracker && npm install
cd ../whatsapp-bot && pip install -r requirements.txt

# 配置Nginx反向代理
sudo nano /etc/nginx/sites-available/medical-chatbot
```

## 🔒 安全配置

### 生产环境安全措施
1. **环境变量保护**
   - 不使用硬编码密钥
   - 使用密钥管理服务
   - 定期轮换密钥

2. **网络安全**
   - 启用HTTPS
   - 配置防火墙规则
   - 使用WAF（Web应用防火墙）

3. **数据保护**
   - 数据库加密
   - 定期备份
   - 访问日志监控

### SSL证书配置
```bash
# 使用Let's Encrypt获取免费SSL证书
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com
```

## 📊 监控和日志

### 应用监控
1. **性能监控**: 使用New Relic或DataDog
2. **错误追踪**: Sentry或Bugsnag
3. **用户分析**: Google Analytics或Mixpanel

### 日志配置
```typescript
// 后端日志配置
import { Logger } from '@nestjs/common';

const logger = new Logger('MedicalChatbot');
logger.log('Application started');
logger.error('Error occurred', error.stack);
```

## 🔄 持续集成/持续部署

### GitHub Actions配置
```yaml
name: Deploy to Production
on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Node.js
      uses: actions/setup-node@v2
      with:
        node-version: '18'
    
    - name: Install dependencies
      run: |
        cd new-fyp-chatbot-nest
        npm ci
    
    - name: Run tests
      run: |
        cd new-fyp-chatbot-nest
        npm test
    
    - name: Deploy to production
      run: |
        # 部署脚本
        echo "Deploying to production..."
```

## 🧪 测试部署

### 预生产环境测试
1. **功能测试**: 验证所有核心功能
2. **性能测试**: 负载测试和压力测试
3. **安全测试**: 渗透测试和漏洞扫描
4. **用户体验测试**: 真实用户测试

### 健康检查端点
```typescript
// 后端健康检查
@Get('health')
getHealth() {
  return {
    status: 'ok',
    timestamp: new Date().toISOString(),
    version: process.env.npm_package_version
  };
}
```

## 📈 运维最佳实践

### 日常运维
1. **监控报警**: 设置关键指标报警
2. **定期备份**: 数据库和应用数据备份
3. **安全更新**: 定期更新依赖和系统
4. **性能优化**: 持续监控和优化性能

### 灾难恢复
1. **备份策略**: 多地域备份
2. **恢复流程**: 明确的恢复步骤
3. **测试演练**: 定期恢复测试

---

## 🎯 下一步行动

### 立即执行
1. [ ] 创建GitHub仓库
2. [ ] 推送清理后的代码
3. [ ] 配置GitHub Actions
4. [ ] 设置生产环境

### 中期计划
1. [ ] 实施监控系统
2. [ ] 配置自动备份
3. [ ] 优化性能
4. [ ] 安全加固

### 长期目标
1. [ ] 扩展功能模块
2. [ ] 多语言支持
3. [ ] 移动应用开发
4. [ ] 第三方集成

**提示**: 部署前请确保所有环境变量已正确配置，并进行充分的测试。