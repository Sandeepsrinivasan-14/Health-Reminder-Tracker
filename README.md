# 💊 Health Reminder & Tracker App

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![React](https://img.shields.io/badge/React-18.2-blue)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)](https://fastapi.tiangolo.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-06B6D4)](https://tailwindcss.com/)

A comprehensive medical reminder and health tracking application designed to help patients manage medications, track vaccinations, and provide emergency support with caregiver monitoring capabilities.

## 📱 Features

### Core Features
- **👤 User Management**: Create and manage multiple patient profiles
- **💊 Medication Tracking**: Add medications with dosage and time-of-day reminders (Morning/Afternoon/Evening)
- **💉 Vaccination Scheduler**: Track upcoming vaccines and immunization schedules
- **🚨 Emergency SOS**: One-tap emergency button with GPS location sharing
- **👥 Caregiver Dashboard**: Monitor patient adherence and health status remotely
- **💡 Health Tips**: Daily health advice and wellness tips

### Technical Features
- RESTful API with FastAPI
- SQLite database for data persistence
- React TypeScript frontend with Tailwind CSS
- Responsive design for mobile and desktop
- Real-time API status monitoring
- Offline-capable Progressive Web App (PWA) ready

## 📸 Screenshots

### Patient Dashboard
![Patient Dashboard](https://via.placeholder.com/800x400?text=Patient+Dashboard)

### Medication Management
![Medications](https://via.placeholder.com/800x400?text=Medication+Management)

### Caregiver Monitoring
![Caregiver View](https://via.placeholder.com/800x400?text=Caregiver+Monitoring)

### SOS Emergency
![SOS Button](https://via.placeholder.com/800x400?text=SOS+Emergency+Button)

## 🛠️ Technology Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development
- **Tailwind CSS** for styling
- **React Hooks** for state management

### Backend
- **FastAPI** Python framework
- **SQLite** database
- **Uvicorn** ASGI server
- **CORS** middleware enabled

## 📋 Prerequisites

- Node.js (v16 or higher)
- Python (v3.8 or higher)
- npm or yarn
- pip (Python package manager)
- Git (for cloning)

## 🚀 Quick Start

### 1. Clone the Repository
\\\ash
git clone https://github.com/Sandeepsrinivasan-14/Health-Reminder-Tracker.git
cd Health-Reminder-Tracker
\\\

### 2. Backend Setup

\\\ash
# Install Python dependencies
pip install -r requirements.txt

# Start the backend server
uvicorn backend:app --reload --host 0.0.0.0 --port 8000
\\\

The backend will run at: http://localhost:8000

### 3. Frontend Setup

Open a new terminal and run:

\\\ash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
\\\

The frontend will run at: http://localhost:5173

### 4. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📖 Usage Guide

### Creating a User
1. Open the Dashboard tab
2. Enter name and email in the "Create / Select User" section
3. Click "Create User"
4. Select the user from the list below

### Adding Medications
1. Select a user from the list
2. Enter medication name and dosage
3. Choose time of day (Morning/Afternoon/Evening)
4. Click "Add Medication"
5. Mark medications as "Taken" or "Missed" as needed

### Scheduling Vaccinations
1. Select a user
2. Enter vaccine name and due date
3. Click "Add Vaccination"
4. View upcoming vaccinations in the list

### Using SOS Emergency
1. Switch to "Caregiver & SOS" tab
2. Click the red "SOS EMERGENCY BUTTON"
3. Allow location access when prompted
4. Emergency alert will be sent with your location

### Caregiver Monitoring
1. Switch to "Caregiver & SOS" tab
2. Select a patient from Dashboard first
3. View patient information, medications, and vaccines
4. Monitor adherence and receive alerts

### Loading Health Tips
1. Go to "Caregiver & SOS" tab
2. Click "Load Health Tips"
3. View daily health advice and wellness tips

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | API health check |
| GET | /users | Get all users |
| POST | /users | Create new user |
| GET | /medications/user/{id} | Get user medications |
| POST | /medications | Add new medication |
| POST | /medications/{id}/log | Log medication status |
| GET | /vaccinations/user/{id} | Get user vaccinations |
| POST | /vaccinations | Add vaccination |
| GET | /health-tips | Get daily health tips |

## 📁 Project Structure

\\\
Health-Reminder-Tracker/
├── backend.py              # FastAPI backend server
├── requirements.txt        # Python dependencies
├── health_tracker.db       # SQLite database (auto-generated)
├── docker-compose.yml      # Docker setup
├── .gitignore             # Git ignore rules
├── README.md              # Project documentation
├── LICENSE                # MIT License
└── frontend/              # React TypeScript frontend
    ├── src/
    │   ├── App.tsx        # Main React component
    │   ├── api.ts         # API integration functions
    │   ├── main.tsx       # Application entry point
    │   └── index.css      # Tailwind CSS styles
    ├── public/
    │   └── vite.svg       # Vite logo
    ├── index.html         # HTML template
    ├── package.json       # Node dependencies
    ├── tsconfig.json      # TypeScript configuration
    ├── vite.config.ts     # Vite configuration
    ├── tailwind.config.js # Tailwind CSS configuration
    └── postcss.config.js  # PostCSS configuration
\\\

## 🐳 Docker Deployment

### Using Docker Compose
\\\ash
# Start all services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f
\\\

## 🧪 Testing the API

### Test Backend Health
\\\ash
curl http://localhost:8000/health
\\\

### Test Creating a User
\\\ash
curl -X POST http://localhost:8000/users \\
  -H "Content-Type: application/json" \\
  -d '{"name":"John Doe","email":"john@example.com"}'
\\\

### Test Getting All Users
\\\ash
curl http://localhost:8000/users
\\\

### Test Adding a Medication
\\\ash
curl -X POST http://localhost:8000/medications \\
  -H "Content-Type: application/json" \\
  -d '{"user_id":1,"name":"Aspirin","dosage":"100mg","time_of_day":"morning","active":true}'
\\\

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (\git checkout -b feature/AmazingFeature\)
3. Commit your changes (\git commit -m 'Add some AmazingFeature'\)
4. Push to the branch (\git push origin feature/AmazingFeature\)
5. Open a Pull Request

## 👥 Team Members

- **Frontend Developer**: UI/UX implementation, React components, Tailwind CSS styling
- **Backend Developer**: API development, database design, FastAPI implementation
- **Integrations & Testing**: API integration, testing, documentation

## 🐛 Troubleshooting

### Backend Won't Start
- Make sure port 8000 is not in use: \
etstat -ano | findstr :8000\
- Check Python version: \python --version\ (needs 3.8+)
- Reinstall dependencies: \pip install -r requirements.txt\

### Frontend Won't Start
- Make sure port 5173 is not in use
- Delete node_modules and reinstall: \m -rf node_modules && npm install\
- Clear npm cache: \
pm cache clean --force\

### API Connection Issues
- Ensure backend is running on http://localhost:8000
- Check CORS settings in backend.py
- Verify API_URL in frontend/src/api.ts is correct

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the excellent Python framework
- [React](https://reactjs.org/) for the amazing frontend library
- [Tailwind CSS](https://tailwindcss.com/) for the utility-first CSS framework
- [Vite](https://vitejs.dev/) for fast development experience
- [SQLite](https://www.sqlite.org/) for lightweight database

## 📞 Support

For issues, questions, or contributions:
- Open an issue on [GitHub Issues](https://github.com/Sandeepsrinivasan-14/Health-Reminder-Tracker/issues)
- Contact the maintainers

---

**Made with ❤️ for better healthcare management**

[Report Bug](https://github.com/Sandeepsrinivasan-14/Health-Reminder-Tracker/issues) · [Request Feature](https://github.com/Sandeepsrinivasan-14/Health-Reminder-Tracker/issues)

## 📊 Project Status

✅ Phase 1: Project Setup  
✅ Phase 2: Backend Development  
✅ Phase 3: Frontend Development  
✅ Phase 4: Integration  
✅ Phase 5: Testing & Deployment  
✅ Phase 6: Documentation

## 🎯 Future Enhancements

- [ ] Push notifications for medication reminders
- [ ] Email/SMS alerts for missed medications
- [ ] Weekly health reports
- [ ] Multiple language support
- [ ] Dark mode
- [ ] Export data to PDF/CSV
- [ ] Integration with fitness trackers
- [ ] Telemedicine integration
- [ ] Prescription scanning
- [ ] Medication interaction checker

---

**⭐ Star this repository if you find it helpful!**
