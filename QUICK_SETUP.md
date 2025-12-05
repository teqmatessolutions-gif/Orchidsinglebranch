# 🚀 QUICK SETUP - ORCHID RESORT SYSTEM

## 📦 What You Need
1. Python 3.8+
2. Node.js 16+
3. PostgreSQL 13+
4. Git

---

## ⚡ Quick Setup (5 Steps)

### 1️⃣ Clone Repository
```bash
git clone https://github.com/teqmatessolutions-gif/completedresort.git
cd completedresort
git checkout orchid_latest
```

### 2️⃣ Setup Backend
```bash
cd ResortApp
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-jose passlib bcrypt python-multipart alembic
```

### 3️⃣ Setup Frontend
```bash
cd ../dasboard
npm install
```

### 4️⃣ Create Database
```sql
-- In PostgreSQL (psql or pgAdmin)
CREATE DATABASE orchid_resort;
```

### 5️⃣ Configure .env
Create `ResortApp/.env`:
```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/orchid_resort
SECRET_KEY=change-this-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## ▶️ Run Application

### Terminal 1 - Backend:
```bash
cd ResortApp
venv\Scripts\activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8011
```

### Terminal 2 - Frontend:
```bash
cd dasboard
npm start
```

### Open Browser:
```
http://localhost:3000
```

---

## 🔧 Run Migrations
```bash
cd ResortApp
python add_department_to_inventory_transactions.py
python backfill_transaction_departments.py
```

---

## 📁 Repository URL
```
https://github.com/teqmatessolutions-gif/completedresort.git
Branch: orchid_latest
```

---

## ✅ Verify Setup
- [ ] Backend running: http://localhost:8011/docs
- [ ] Frontend running: http://localhost:3000
- [ ] Database connected
- [ ] Can login to system

---

## 🆘 Common Issues

**"Module not found"**
→ Run `pip install -r requirements.txt` or `npm install`

**"Database connection failed"**
→ Check PostgreSQL is running and .env has correct password

**"Port already in use"**
→ Kill existing process or use different port

---

**For detailed instructions, see SETUP_GUIDE.md**
