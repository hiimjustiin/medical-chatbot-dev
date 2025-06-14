module.exports = {
  apps: [
    {
      name: 'backend-api',
      cwd: './new-fyp-chatbot-nest',
      script: 'npm',
      args: 'run start:prod',
      env: { PORT: 3005, NODE_ENV: 'production' }
    },
    {
      name: 'whatsapp-bot',
      cwd: './whatsapp-bot',
      script: 'main.py',
      exec_interpreter: '/home/ubuntu/medical-chatbot-dev/whatsapp-bot/venv/bin/python3',
      exec_mode: 'fork',
      env: { PORT: 3001 }
    },  // ← 这里一定要有逗号！
    {
      name: 'patient-tracker',
      cwd: './patient-tracker',
      script: 'npm',
      args: 'run start -- -p 3000',
      env: { NODE_ENV: 'production' }
    }
  ]
};

