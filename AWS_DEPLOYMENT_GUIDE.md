# AWS部署指南 - 使用Termius

## 🎯 快速部署步骤

### 第一步：AWS EC2实例准备

**1. 登录AWS控制台**
- 访问 https://console.aws.amazon.com
- 选择EC2服务

**2. 启动EC2实例**
```
实例配置：
- AMI: Ubuntu Server 22.04 LTS
- 实例类型: t3.medium (2vCPU, 4GB内存)
- 存储: 30GB GP3
- 安全组: 开放端口 22, 80, 443, 3000, 3001, 5000
```

**3. 下载密钥对**
- 创建新的密钥对或使用现有
- 下载.pem文件到本地
- 妥善保存密钥文件

### 第二步：Termius配置

**1. 安装Termius**
- 从官网下载Termius: https://termius.com
- 安装并打开应用

**2. 配置连接**
```
新建主机配置：
- 标签: Medical-Chatbot-AWS
- 地址: [你的EC2公有IP]
- 用户名: ubuntu
- 端口: 22
- 认证: 使用下载的.pem密钥文件
```

**3. 测试连接**
- 点击连接按钮
- 确认成功登录到服务器

### 第三步：一键部署脚本

通过Termius连接到服务器后，执行以下命令：

```bash
# 下载并运行部署脚本
wget https://raw.githubusercontent.com/your-username/medical-chatbot-system/main/deploy.sh
chmod +x deploy.sh
./deploy.sh
```

或者手动执行以下步骤：

## 🔧 手动部署步骤

### 1. 系统环境设置

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础工具
sudo apt install -y curl wget git vim htop

# 设置时区
sudo timedatectl set-timezone Asia/Shanghai
```

### 2. 安装Node.js环境

```bash
# 安装Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 验证安装
node --version
npm --version
```

### 3. 安装Python环境

```bash
# 安装Python 3.10+
sudo apt install -y python3 python3-pip python3-venv

# 验证安装
python3 --version
pip3 --version
```

### 4. 安装进程管理工具

```bash
# 安装PM2
sudo npm install -g pm2

# 配置PM2开机自启
pm2 startup
sudo env PATH=$PATH:/usr/bin /usr/lib/node_modules/pm2/bin/pm2 startup systemd -u ubuntu --hp /home/ubuntu
```

### 5. 安装Web服务器

```bash
# 安装Nginx
sudo apt install -y nginx

# 启动Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 6. 部署应用程序

```bash
# 创建应用目录
sudo mkdir -p /opt/medical-chatbot
sudo chown ubuntu:ubuntu /opt/medical-chatbot
cd /opt/medical-chatbot

# 克隆代码
git clone https://github.com/your-username/medical-chatbot-system.git .
```

### 7. 配置环境变量

```bash
# 创建环境变量文件
sudo nano /opt/medical-chatbot/.env

# 添加以下内容（根据实际情况修改）
NODE_ENV=production
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
OPENAI_API_KEY=your_openai_key
META_ACCESS_TOKEN=your_meta_token
META_PHONE_NUMBER_ID=your_phone_id
WEBHOOK_VERIFY_TOKEN=your_verify_token
```

### 8. 部署后端服务

```bash
cd /opt/medical-chatbot/new-fyp-chatbot-nest

# 安装依赖
npm install --production

# 构建应用
npm run build

# 使用PM2启动
pm2 start npm --name "medical-backend" -- run start:prod
```

### 9. 部署前端服务

```bash
cd /opt/medical-chatbot/patient-tracker

# 安装依赖
npm install --production

# 构建应用
npm run build

# 使用PM2启动
pm2 start npm --name "medical-frontend" -- run start
```

### 10. 部署WhatsApp机器人

```bash
cd /opt/medical-chatbot/whatsapp-bot

# 安装依赖
pip3 install -r requirements.txt

# 使用PM2启动
pm2 start python3 --name "whatsapp-bot" -- main.py
```

### 11. 配置Nginx反向代理

```bash
# 创建Nginx配置
sudo nano /etc/nginx/sites-available/medical-chatbot
```

添加以下配置：
```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名

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
sudo nginx -t  # 测试配置
sudo systemctl restart nginx
```

### 12. 配置SSL证书

```bash
# 安装Certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d your-domain.com

# 设置自动续期
sudo certbot renew --dry-run
```

## 🚀 自动化部署脚本

创建一键部署脚本 `deploy.sh`：

```bash
#!/bin/bash

set -e  # 遇到错误立即退出

echo "🚀 开始部署医疗聊天机器人系统..."

# 更新系统
echo "📦 更新系统包..."
sudo apt update && sudo apt upgrade -y

# 安装基础依赖
echo "🔧 安装基础工具..."
sudo apt install -y curl wget git vim

# 安装Node.js
echo "📄 安装Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 安装PM2
echo "⚙️ 安装PM2..."
sudo npm install -g pm2

# 安装Nginx
echo "🌐 安装Nginx..."
sudo apt install -y nginx

# 创建应用目录
echo "📁 创建应用目录..."
sudo mkdir -p /opt/medical-chatbot
sudo chown ubuntu:ubuntu /opt/medical-chatbot
cd /opt/medical-chatbot

# 克隆代码
echo "📥 克隆代码..."
git clone https://github.com/your-username/medical-chatbot-system.git .

# 部署后端
echo "🔙 部署后端服务..."
cd new-fyp-chatbot-nest
npm install --production
npm run build
pm2 start npm --name "medical-backend" -- run start:prod

# 部署前端
echo "🔜 部署前端服务..."
cd ../patient-tracker
npm install --production
npm run build
pm2 start npm --name "medical-frontend" -- run start

# 部署WhatsApp机器人
echo "🤖 部署WhatsApp机器人..."
cd ../whatsapp-bot
pip3 install -r requirements.txt
pm2 start python3 --name "whatsapp-bot" -- main.py

# 保存PM2配置
pm2 save

# 配置开机自启
sudo env PATH=$PATH:/usr/bin /usr/lib/node_modules/pm2/bin/pm2 startup systemd -u ubuntu --hp /home/ubuntu

echo "✅ 部署完成！"
echo "📊 服务状态："
pm2 status
```

## 🔍 监控和维护

### 服务状态检查

```bash
# 查看所有服务状态
pm2 status

# 查看单个服务日志
pm2 logs medical-backend
pm2 logs medical-frontend  
pm2 logs whatsapp-bot

# 实时监控
pm2 monit
```

### 系统资源监控

```bash
# 查看系统资源
htop

# 查看磁盘使用
df -h

# 查看内存使用
free -h
```

### 日志管理

```bash
# 设置日志轮转
sudo nano /etc/logrotate.d/medical-chatbot

# 添加以下内容
/opt/medical-chatbot/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}

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

## 🛠️ 故障排除

### 常见问题解决

**1. 服务无法启动**
```bash
# 检查端口占用
sudo netstat -tulpn | grep :3000

# 重启服务
pm2 restart service-name

# 重新安装依赖
cd /opt/medical-chatbot/new-fyp-chatbot-nest
rm -rf node_modules
npm install
```

**2. Nginx配置错误**
```bash
# 测试配置
sudo nginx -t

# 查看错误日志
sudo tail -f /var/log/nginx/error.log
```

**3. 数据库连接问题**
- 检查Supabase连接配置
- 验证网络连接
- 检查防火墙设置

### 性能优化

**1. 增加交换空间**
```bash
# 创建交换文件
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 永久生效
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

**2. 优化Nginx配置**
```bash
sudo nano /etc/nginx/nginx.conf

# 在http块中添加
worker_processes auto;
worker_connections 1024;
keepalive_timeout 65;
```

## 📈 扩展和升级

### 水平扩展
```bash
# 创建新的EC2实例
# 使用相同的部署脚本
# 配置负载均衡器
```

### 应用升级
```bash
# 进入应用目录
cd /opt/medical-chatbot

# 拉取最新代码
git pull

# 重新部署
pm2 restart all
```

## 💰 成本优化

### AWS成本控制
- 使用预留实例
- 启用自动缩放
- 监控资源使用
- 使用S3存储日志

### 性能与成本平衡
- 选择合适的实例类型
- 使用Spot实例（非生产环境）
- 优化数据库查询
- 启用缓存

---

## 🎯 下一步

1. **测试部署** - 验证所有服务正常运行
2. **配置域名** - 设置DNS解析到EC2实例
3. **设置监控** - 配置CloudWatch监控
4. **备份策略** - 设置自动备份
5. **安全加固** - 应用安全最佳实践

**提示**: 部署完成后，立即测试所有功能，确保系统稳定运行。