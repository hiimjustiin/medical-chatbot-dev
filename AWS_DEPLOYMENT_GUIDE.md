# AWS Deployment Guide - Using Termius

## 🎯 Quick Deployment Steps

### Step 1: AWS EC2 Instance Preparation

**1. Log in to AWS Console**

- Visit https://console.aws.amazon.com
- Select EC2 Service

**2. Launch EC2 Instance**

```
Instance Configuration:
- AMI: Ubuntu Server 22.04 LTS
- Instance Type: t3.medium (2vCPU, 4GB RAM)
- Storage: 30GB GP3
- Security Group: Open ports 22, 80, 443, 3000, 3001, 5000
```

**3. Download Key Pair**

- Create a new key pair or use an existing one
- Download the .pem file to your local machine
- Save the key file securely

### Step 2: Termius Configuration

**1. Install Termius**

- Download Termius from the official website: https://termius.com
- Install and open the application

**2. Configure Connection**

```
New Host Configuration:
- Label: Medical-Chatbot-AWS
- Address: [Your EC2 Public IP]
- Username: ubuntu
- Port: 22
- Authentication: Use the downloaded .pem key file
```

**3. Test Connection**

- Click the connect button
- Confirm successful login to the server

### Step 3: One-Click Deployment Script

After connecting to the server via Termius, execute the following command:

```bash
# Download and run the deployment script
wget https://raw.githubusercontent.com/your-username/medical-chatbot-system/main/deploy.sh
chmod +x deploy.sh
./deploy.sh
```

Or manually execute the following steps:

## 🔧 Manual Deployment Steps

### 1. System Environment Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install basic tools
sudo apt install -y curl wget git vim htop

# Set timezone
sudo timedatectl set-timezone Asia/Shanghai
```

### 2. Install Node.js Environment

```bash
# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version
npm --version
```

### 3. Install Python Environment

```bash
# Install Python 3.10+
sudo apt install -y python3 python3-pip python3-venv

# Verify installation
python3 --version
pip3 --version
```

### 4. Install Process Management Tool

```bash
# Install PM2
sudo npm install -g pm2

# Configure PM2 to start on boot
pm2 startup
sudo env PATH=$PATH:/usr/bin /usr/lib/node_modules/pm2/bin/pm2 startup systemd -u ubuntu --hp /home/ubuntu
```

### 5. Install Web Server

```bash
# Install Nginx
sudo apt install -y nginx

# Start Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 6. Deploy Application

```bash
# Create application directory
sudo mkdir -p /opt/medical-chatbot
sudo chown ubuntu:ubuntu /opt/medical-chatbot
cd /opt/medical-chatbot

# Clone code
git clone https://github.com/your-username/medical-chatbot-system.git .
```

### 7. Configure Environment Variables

```bash
# Create environment variable file
sudo nano /opt/medical-chatbot/.env

# Add the following content (modify according to actual situation)
NODE_ENV=production
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
OPENAI_API_KEY=your_openai_key
META_ACCESS_TOKEN=your_meta_token
META_PHONE_NUMBER_ID=your_phone_id
WEBHOOK_VERIFY_TOKEN=your_verify_token
```

### 8. Deploy Backend Service

```bash
cd /opt/medical-chatbot/new-fyp-chatbot-nest

# Install dependencies
npm install --production

# Build application
npm run build

# Start using PM2
pm2 start npm --name "medical-backend" -- run start:prod
```

### 9. Deploy Frontend Service

```bash
cd /opt/medical-chatbot/patient-tracker

# Install dependencies
npm install --production

# Build application
npm run build

# Start using PM2
pm2 start npm --name "medical-frontend" -- run start
```

### 10. Deploy WhatsApp Bot

```bash
cd /opt/medical-chatbot/whatsapp-bot

# Install dependencies
pip3 install -r requirements.txt

# Start using PM2
pm2 start python3 --name "whatsapp-bot" -- main.py
```

### 11. Configure Nginx Reverse Proxy

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/medical-chatbot
```

Add the following configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名

    # Frontend Service
    location / {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
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

Enable configuration:

```bash
sudo ln -s /etc/nginx/sites-available/medical-chatbot /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl restart nginx
```

### 12. Configure SSL Certificate

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Set up automatic renewal
sudo certbot renew --dry-run
```

## 🚀 Automation Deployment Script

Create one-click deployment script `deploy.sh`:

```bash
#!/bin/bash

set -e  # Exit immediately if an error occurs

echo "🚀 Starting deployment of Medical Chatbot System..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install basic dependencies
echo "🔧 Installing basic tools..."
sudo apt install -y curl wget git vim

# Install Node.js
echo "📄 Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install PM2
echo "⚙️ Installing PM2..."
sudo npm install -g pm2

# Install Nginx
echo "🌐 Installing Nginx..."
sudo apt install -y nginx

# Create application directory
echo "📁 Creating application directory..."
sudo mkdir -p /opt/medical-chatbot
sudo chown ubuntu:ubuntu /opt/medical-chatbot
cd /opt/medical-chatbot

# Clone code
echo "📥 Cloning code..."
git clone https://github.com/your-username/medical-chatbot-system.git .

# Deploy Backend
echo "🔙 Deploying backend service..."
cd new-fyp-chatbot-nest
npm install --production
npm run build
pm2 start npm --name "medical-backend" -- run start:prod

# Deploy Frontend
echo "🔜 Deploying frontend service..."
cd ../patient-tracker
npm install --production
npm run build
pm2 start npm --name "medical-frontend" -- run start

# Deploy WhatsApp Bot
echo "🤖 Deploying WhatsApp bot..."
cd ../whatsapp-bot
pip3 install -r requirements.txt
pm2 start python3 --name "whatsapp-bot" -- main.py

# Save PM2 configuration
pm2 save

# Configure start on boot
sudo env PATH=$PATH:/usr/bin /usr/lib/node_modules/pm2/bin/pm2 startup systemd -u ubuntu --hp /home/ubuntu

echo "✅ Deployment complete!"
echo "📊 Service Status:"
pm2 status
```

## 🔍 Monitoring and Maintenance

### Service Status Check

```bash
# View status of all services
pm2 status

# View individual service logs
pm2 logs medical-backend
pm2 logs medical-frontend  
pm2 logs whatsapp-bot

# Real-time monitoring
pm2 monit
```

### System Resource Monitoring

```bash
# View system resources
htop

# View disk usage
df -h

# View memory usage
free -h
```

### Log Management

```bash
# Set up log rotation
sudo nano /etc/logrotate.d/medical-chatbot

# Add the following content
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

## 🛠️ Troubleshooting

### Common Problem Solving

**1. Service fails to start**

```bash
# Check port occupancy
sudo netstat -tulpn | grep :3000

# Restart service
pm2 restart service-name

# Reinstall dependencies
cd /opt/medical-chatbot/new-fyp-chatbot-nest
rm -rf node_modules
npm install
```

**2. Nginx configuration error**

```bash
# Test configuration
sudo nginx -t

# View error logs
sudo tail -f /var/log/nginx/error.log
```

**3. Database connection issues**

- Check Supabase connection configuration
- Verify network connection
- Check firewall settings

### Performance Optimization

**1. Increase Swap space**

```bash
# Create swap file
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

**2. Optimize Nginx configuration**

```bash
sudo nano /etc/nginx/nginx.conf

# Add to the http block
worker_processes auto;
worker_connections 1024;
keepalive_timeout 65;
```

## 📈 Expansion and Upgrading

### Horizontal Scaling

```bash
# Create new EC2 instances
# Use the same deployment script
# Configure Load Balancer
```

### Application Upgrade

```bash
# Enter application directory
cd /opt/medical-chatbot

# Pull latest code
git pull

# Redeploy
pm2 restart all
```

## 💰 Cost Optimization

### AWS Cost Control

* Use Reserved Instances
* Enable Auto Scaling
* Monitor resource usage
* Use S3 for log storage

### Performance and Cost Balance

* Choose appropriate instance types
* Use Spot instances (non-production environments)
* Optimize database queries
* Enable caching

---

## 🎯 Next Steps

1. **Test Deployment** - Verify all services are running correctly
2. **Configure Domain** - Set DNS resolution to EC2 instance
3. **Set up Monitoring** - Configure CloudWatch monitoring
4. **Backup Strategy** - Set up automatic backups
5. **Security Hardening** - Apply security best practices

**Tip** : After deployment is complete, immediately test all functions to ensure the system is running stably.

*For the original Chinese documentation, please see AWS_DEPLOYMENT_GUIDECN.md*
