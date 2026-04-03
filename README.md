# 🏥 Medical Health Reminder Tracker

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.2.0-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com/)
[![Gemini AI](https://img.shields.io/badge/Gemini_AI-Integrated-4285F4.svg)](https://deepmind.google/technologies/gemini/)

## 📋 Overview

**Medical Health Reminder Tracker** is a comprehensive AI-powered healthcare management system that helps patients track their health metrics, receive personalized health advice, set medication reminders, and trigger emergency alerts. The system integrates Google's Gemini AI for intelligent health assistance and Twilio for SMS emergency notifications.

### 🎯 Key Features

| Category | Features |
|----------|----------|
| **Health Tracking** | BP, Heart Rate, Blood Sugar, Weight monitoring |
| **AI Integration** | Gemini AI chat, Risk prediction, Personalized health tips |
| **Emergency** | SOS SMS alerts via Twilio, WhatsApp ready |
| **Reminders** | Medication reminders, Vaccination tracking |
| **Reports** | PDF, JSON, CSV export, Email preview |
| **User Management** | Multi-user support, 22+ test profiles |
| **UI/UX** | Dark/Light theme, Responsive design, Glassmorphism |

---

## 🚀 Live Demo

- **Frontend:** https://health-tracker-frontend.vercel.app
- **Backend API:** https://health-tracker-backend.onrender.com
- **API Documentation:** https://health-tracker-backend.onrender.com/docs

---

## 📸 Screenshots

### Dashboard Light Mode
![Light Mode Dashboard](https://via.placeholder.com/800x400?text=Light+Mode+Dashboard)

### Dark Mode Interface
![Dark Mode Dashboard](https://via.placeholder.com/800x400?text=Dark+Mode+Interface)

### AI Chat Assistant
![AI Chat](https://via.placeholder.com/800x400?text=AI+Chat+Assistant)

---

## 🛠️ Tech Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11 | Core language |
| FastAPI | 0.104.1 | REST API framework |
| SQLite3 | - | Database |
| Uvicorn | 0.24.0 | ASGI server |
| Google Gemini AI | - | AI health assistant |
| Twilio | 8.10.4 | SMS notifications |
| ReportLab | 4.0.4 | PDF generation |

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.2.0 | UI framework |
| Vite | 5.4.21 | Build tool |
| Chart.js | 4.4.0 | Health analytics |
| React Icons | 5.0.1 | Icon library |

---

## 📁 Project Structure
HealthReminderTracker/
├── backend.py # FastAPI backend server
├── ai_service.py # Gemini AI integration
├── twilio_service.py # SMS notification service
├── health_tracker.db # SQLite database
├── requirements.txt # Python dependencies
├── .env # Environment variables
├── frontend/
│ ├── src/
│ │ ├── App.jsx # Main React component
│ │ ├── components/ # Reusable components
│ │ │ ├── SOSButton.jsx
│ │ │ ├── HealthRecords.jsx
│ │ │ └── NotificationBell.jsx
│ │ └── services/
│ │ └── NotificationService.js
│ ├── public/
│ └── package.json
└── README.md


---

## 🔧 Installation

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn

### Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/Medical-Health-Tracker.git
cd Medical-Health-Tracker





Backend Setup
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Update .env with your credentials
# - GEMINI_API_KEY
# - TWILIO_ACCOUNT_SID
# - TWILIO_AUTH_TOKEN
# - TWILIO_PHONE_NUMBER

# Run backend
uvicorn backend:app --reload --host 0.0.0.0 --port 8000




Frontend Setup
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev



Access Application
Frontend: http://localhost:5173

Backend API: http://localhost:8000

API Docs: http://localhost:8000/docs





🌍 Deployment
Backend (Render)
Push code to GitHub

Create account on Render

Click "New +" → "Web Service"

Connect your GitHub repository

Configure:

Build Command: pip install -r requirements.txt

Start Command: uvicorn backend:app --host 0.0.0.0 --port $PORT

Add environment variables

Click "Deploy"

Frontend (Vercel)
bash
cd frontend
npm install -g vercel
vercel --prod
🔐 Environment Variables
Create .env file with:

env
# Gemini AI
GEMINI_API_KEY=your_gemini_api_key

# Twilio SMS
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+15187194160

# Caregiver Contact
CARETAKER_PHONE=+91xxxxxxxxxx
📊 API Endpoints
MethodEndpointDescription
GET/healthHealth check
GET/usersGet all users
POST/usersCreate user
POST/health-dataSave health data
GET/health-data/user/{id}Get user health data
POST/api/ai/chatAI chat assistant
POST/api/ai/health-riskHealth risk prediction
POST/api/ai/health-tipsAI personalized tips
POST/sosSend SOS alert
GET/export-pdf/{id}Download PDF report
GET/api/download-report/{id}Download JSON/CSV
🧪 Testing
bash
# Run backend tests
python test_notifications.py

# Run complete test suite
python complete_test_suite.py

# Check API status
curl http://localhost:8000/health
📈 Features in Detail
🤖 AI Health Assistant
Conversational AI powered by Google Gemini

Context-aware responses with conversation memory

Personalized health advice based on user data

🚨 Emergency SOS
One-click emergency alert

Instant SMS to caregiver via Twilio

WhatsApp integration ready

📊 Health Analytics
Real-time health metrics tracking

Historical data visualization

Risk level prediction

Personalized recommendations

🔔 Notification System
Medication reminders

Vaccination alerts

Low stock warnings

Health metric alerts

📄 Reports
PDF health reports

JSON data export

CSV for Excel

Email preview

🤝 Contributing
Contributions are welcome! Please follow these steps:

Fork the repository

Create feature branch (git checkout -b feature/AmazingFeature)

Commit changes (git commit -m 'Add AmazingFeature')

Push to branch (git push origin feature/AmazingFeature)

Open Pull Request

📄 License
Distributed under the MIT License. See LICENSE for more information.

👨‍💻 Author
Your Name

GitHub: https://github.com/Sandeepsrinivasan-14

Email: sndpsrinivasan@gmail.com

🙏 Acknowledgments
Google Gemini AI for intelligent health assistance

Twilio for SMS notifications

FastAPI community

React ecosystem

⭐ Support
If you found this project helpful, please give it a ⭐ on GitHub!

📞 Contact
For questions or support, please open an issue on GitHub.

Built with ❤️ for better healthcare 🏥
