# Medical Chatbot System

A comprehensive medical health management platform featuring a patient tracking dashboard, a WhatsApp automated messaging system, and AI-driven personalised health recommendations.

## 🏗️ Project Architecture

This project adopts a microservices architecture consisting of three main components:

### 1. Backend Service (NestJS)
- **Location**: `new-fyp-chatbot-nest/`
- **Tech Stack**: NestJS, TypeScript, Supabase
- **Functions**: RESTful API, patient data management, exercise plan assignment, GPT integration

### 2. Frontend Dashboard (Next.js)
- **Location**: `patient-tracker/`
- **Tech Stack**: Next.js 14, React, Tailwind CSS, Radix UI
- **Functions**: Patient management interface, data visualisation, report uploading

### 3. WhatsApp Bot (Python)
- **Location**: `whatsapp-bot/`
- **Tech Stack**: Python, Flask, Meta WhatsApp API
- **Functions**: Automated message sending, health reminders, personalised communication.

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

## 🤖 AI Personalised Response System

### Core Features
1. **Patient Profiling** - Build health profiles based on historical data
2. **Personalised Advice** - Provide customised health suggestions based on patient conditions
3. **Smart Reminders** - Intelligent reminder system based on behaviour patterns
4. **Sentiment Analysis** - Analyse patient emotional states to adjust communication strategies

### Implementation Mechanism
- **GPT Integration**: AI dialogue implemented via the GPT module
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

## 🔒 Security Features

- JWT Authentication
- Encrypted data storage
- API Access Control
- Input validation and sanitisation

## 📈 Monitoring and Logs

- Application Performance Monitoring (APM)
- Error logging
- User behaviour analysis
- System health checks

## 🧪 Testing

### Running Tests
```bash
# Backend Tests
cd new-fyp-chatbot-nest
npm test

# Frontend Tests
cd patient-tracker
npm test

# WhatsApp Bot Tests
cd whatsapp-bot
python -m pytest
```

## 🚢 Deployment

### Production Deployment
1. **Backend**: Deploy using PM2 or Docker.
2. **Frontend**: Deploy via Vercel or Netlify.
3. **Bot**: Deploy on a Cloud Server.

### Environment Configuration
- Production environment variable settings
- SSL Certificate configuration
- Database backup strategy
- Monitoring and alert settings

## 🤝 Contribution Guide

1. Fork the project
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For questions or suggestions, please contact us via:
- Creating an Issue
- Emailing the project maintainer
- Checking the documentation for more information

---

**Note**: This project involves medical health data; please ensure compliance with relevant privacy regulations and data protection laws.
