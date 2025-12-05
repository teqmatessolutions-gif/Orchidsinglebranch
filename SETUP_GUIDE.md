# 🚀 PROJECT SETUP GUIDE - ORCHID RESORT MANAGEMENT SYSTEM

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Clone the Repository](#clone-the-repository)
3. [Backend Setup (FastAPI)](#backend-setup-fastapi)
4. [Frontend Setup (React)](#frontend-setup-react)
5. [Database Setup (PostgreSQL)](#database-setup-postgresql)
6. [Running the Application](#running-the-application)
7. [Troubleshooting](#troubleshooting)

---

## 1. Prerequisites

### Required Software:
- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **Node.js 16+** - [Download](https://nodejs.org/)
- **PostgreSQL 13+** - [Download](https://www.postgresql.org/download/)
- **Git** - [Download](https://git-scm.com/downloads/)

### Verify Installation:
```bash
python --version    # Should show Python 3.8+
node --version      # Should show v16+
npm --version       # Should show 8+
psql --version      # Should show PostgreSQL 13+
git --version       # Should show Git 2.x+
```

---

## 2. Clone the Repository

### Option 1: From GitHub (Recommended)
```bash
# Clone the repository
git clone https://github.com/teqmatessolutions-gif/completedresort.git

# Navigate to the project folder
cd completedresort

# Switch to the latest branch
git checkout orchid_latest
```

### Option 2: From Local Copy
If you have a local copy, just copy the entire `orchid` folder to your new system.

---

## 3. Backend Setup (FastAPI)

### Step 1: Navigate to Backend Directory
```bash
cd ResortApp
```

### Step 2: Create Virtual Environment
**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Python Dependencies
```bash
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist, install manually:
```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-jose passlib bcrypt python-multipart alembic
```

### Step 4: Configure Environment Variables
Create a `.env` file in the `ResortApp` folder:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/orchid_resort

# JWT Secret (generate a random string)
SECRET_KEY=your-secret-key-here-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Settings
DEBUG=True
```

**Important:** Replace `YOUR_PASSWORD` with your PostgreSQL password!

---

## 4. Frontend Setup (React)

### Step 1: Navigate to Frontend Directory
```bash
cd ../dasboard
```

### Step 2: Install Node Dependencies
```bash
npm install
```

This will install all required packages including:
- React
- Recharts (for charts)
- Lucide React (for icons)
- React CountUp
- Framer Motion
- Axios

### Step 3: Configure API URL
Check `dasboard/src/services/api.js` and ensure the base URL is correct:

```javascript
const API_BASE_URL = "http://localhost:8011";
```

---

## 5. Database Setup (PostgreSQL)

### Step 1: Create Database
Open PostgreSQL command line (psql) or pgAdmin:

```sql
-- Create database
CREATE DATABASE orchid_resort;

-- Connect to database
\c orchid_resort

-- Verify connection
SELECT current_database();
```

### Step 2: Run Database Migrations
Go back to the `ResortApp` folder:

```bash
cd ../ResortApp

# Run the migration to add department column
python add_department_to_inventory_transactions.py

# Backfill existing data
python backfill_transaction_departments.py
```

### Step 3: Create Initial User (Optional)
If you need to create an admin user, you can run a Python script or use the API.

---

## 6. Running the Application

### Terminal 1: Start Backend (FastAPI)
```bash
# Navigate to backend
cd ResortApp

# Activate virtual environment (if not already active)
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Start the server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8011
```

**Backend will run on:** `http://localhost:8011`

### Terminal 2: Start Frontend (React)
```bash
# Navigate to frontend
cd dasboard

# Start the development server
npm start
```

**Frontend will run on:** `http://localhost:3000`

### Access the Application
Open your browser and go to:
```
http://localhost:3000
```

---

## 7. Project Structure

```
completedresort/
├── ResortApp/                          # Backend (FastAPI)
│   ├── app/
│   │   ├── api/                        # API endpoints
│   │   │   ├── account.py
│   │   │   ├── dashboard.py
│   │   │   └── ...
│   │   ├── curd/                       # Database operations
│   │   │   ├── inventory.py
│   │   │   ├── service.py
│   │   │   └── ...
│   │   ├── models/                     # Database models
│   │   │   ├── inventory.py
│   │   │   └── ...
│   │   └── utils/                      # Utilities
│   ├── main.py                         # FastAPI app entry point
│   ├── .env                            # Environment variables
│   └── requirements.txt                # Python dependencies
│
└── dasboard/                           # Frontend (React)
    ├── src/
    │   ├── pages/                      # React pages
    │   │   ├── Account.jsx             # Department financial overview
    │   │   ├── Dashboard.jsx
    │   │   └── ...
    │   ├── services/                   # API services
    │   │   └── api.js
    │   └── App.js                      # Main React component
    ├── package.json                    # Node dependencies
    └── public/
```

---

## 8. Troubleshooting

### Backend Issues

**Problem: "ModuleNotFoundError: No module named 'fastapi'"**
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**Problem: "Could not connect to database"**
```bash
# Solution: Check PostgreSQL is running
# Windows: Check Services
# Linux/Mac: sudo systemctl status postgresql

# Verify .env file has correct DATABASE_URL
```

**Problem: "Port 8011 already in use"**
```bash
# Solution: Kill the process or use a different port
python -m uvicorn main:app --reload --port 8012
```

### Frontend Issues

**Problem: "npm: command not found"**
```bash
# Solution: Install Node.js from nodejs.org
```

**Problem: "Module not found" errors**
```bash
# Solution: Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Problem: "Cannot connect to backend"**
```bash
# Solution: Verify backend is running on port 8011
# Check src/services/api.js has correct URL
```

### Database Issues

**Problem: "relation does not exist"**
```bash
# Solution: Run migrations
python add_department_to_inventory_transactions.py
```

**Problem: "password authentication failed"**
```bash
# Solution: Update .env file with correct PostgreSQL password
```

---

## 9. Default Credentials

After setting up, you may need to create an admin user. Check with your team for default credentials or create one through the API.

---

## 10. Important Files to Configure

1. **ResortApp/.env** - Database and JWT settings
2. **dasboard/src/services/api.js** - Backend API URL
3. **PostgreSQL** - Database connection

---

## 11. Quick Start Script

Create a file `setup.sh` (Linux/Mac) or `setup.bat` (Windows):

**Windows (setup.bat):**
```batch
@echo off
echo Setting up Orchid Resort Management System...

echo.
echo [1/5] Creating Python virtual environment...
cd ResortApp
python -m venv venv
call venv\Scripts\activate

echo.
echo [2/5] Installing Python dependencies...
pip install -r requirements.txt

echo.
echo [3/5] Installing Node dependencies...
cd ..\dasboard
npm install

echo.
echo [4/5] Setup complete!
echo.
echo To start the application:
echo   1. Start Backend: cd ResortApp && venv\Scripts\activate && python -m uvicorn main:app --reload --port 8011
echo   2. Start Frontend: cd dasboard && npm start
echo.
pause
```

**Linux/Mac (setup.sh):**
```bash
#!/bin/bash
echo "Setting up Orchid Resort Management System..."

echo ""
echo "[1/5] Creating Python virtual environment..."
cd ResortApp
python3 -m venv venv
source venv/bin/activate

echo ""
echo "[2/5] Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "[3/5] Installing Node dependencies..."
cd ../dasboard
npm install

echo ""
echo "[4/5] Setup complete!"
echo ""
echo "To start the application:"
echo "  1. Start Backend: cd ResortApp && source venv/bin/activate && python -m uvicorn main:app --reload --port 8011"
echo "  2. Start Frontend: cd dasboard && npm start"
```

---

## 12. Production Deployment

For production deployment, you'll need:

1. **Backend:**
   - Use Gunicorn with Uvicorn workers
   - Set DEBUG=False in .env
   - Use environment variables for secrets
   - Set up HTTPS with SSL certificate

2. **Frontend:**
   - Build production bundle: `npm run build`
   - Serve with Nginx or Apache
   - Configure CORS properly

3. **Database:**
   - Use managed PostgreSQL (AWS RDS, Azure Database, etc.)
   - Enable SSL connections
   - Regular backups

---

## 13. Support

If you encounter any issues:
1. Check the logs in terminal
2. Verify all prerequisites are installed
3. Ensure PostgreSQL is running
4. Check .env file configuration

---

## ✅ Checklist

- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] PostgreSQL 13+ installed
- [ ] Git installed
- [ ] Repository cloned
- [ ] Python dependencies installed
- [ ] Node dependencies installed
- [ ] Database created
- [ ] .env file configured
- [ ] Migrations run
- [ ] Backend running on port 8011
- [ ] Frontend running on port 3000
- [ ] Can access http://localhost:3000

---

**🎉 You're all set! The Orchid Resort Management System should now be running on your new system.**
