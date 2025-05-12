# 🏠 Household Services Application - Version 2

A multi-user web application platform offering comprehensive household servicing and solutions. The system integrates user management, backend APIs, Celery tasks, Redis-based caching and rate limiting, and a Vue.js frontend.

---

## 📁 Project Setup

### 1. Clone and Setup Virtual Environment

```bash
cd Household-Services-Application-Version-2
python -m venv venv
venv\Scripts\activate     # On Windows
source venv/bin/activate  # On Linux/macOS
pip install -r requirements.txt
```

---

## ✉️ Email Configuration (Flask-Mail)

1. Go to [Google App Passwords](https://myaccount.google.com/apppasswords).
2. Create a new app password named **"Flask Mail"**.
3. Use the generated password and your Gmail address to update the `Config` class in `config.py`:

```python
MAIL_USERNAME = 'your_email@gmail.com'
MAIL_PASSWORD = 'your_generated_app_password'
MAIL_DEFAULT_SENDER = 'your_email@gmail.com'
```

---

## 🗄️ Database Setup

### Initialize and Migrate

```bash
cd backend
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Create Admin User (in Flask shell)

```python
from app import db
from app.models import Admin

new_admin = Admin(username="username")
new_admin.set_password("password")
db.session.add(new_admin)
db.session.commit()
```

### Query Admin Users

```python
Admin.query.all()
```

---

## ⏱️ Scheduler Setup

In `run.py`:

1. Import at the top:

```python
from app.scheduler import start_scheduler
```

2. After `app.run(debug=True)` in the `__name__ == "__main__"` block:

```python
start_scheduler()
```

---

## 🌿 Redis Setup (for Caching, Rate Limiting & Celery)

Ensure Redis is running before starting the backend:

```bash
# Start Redis (in WSL or Linux terminal)
redis-server

# Stop Redis if needed
sudo systemctl stop redis
```

If you **do not want to use Redis**, comment out these lines in `config.py`:

```python
# CACHE_TYPE = "RedisCache"
# CACHE_DEFAULT_TIMEOUT = 300
# CACHE_REDIS_URL = "redis://localhost:6379/0"

# RATELIMIT_STORAGE_URL = "redis://localhost:6379/0"
```

---

## 🧵 Celery Task Management

### Start Celery Worker

```bash
celery -A celery_worker.celery worker --loglevel=info --pool=solo
```

### Manually Call Celery Tasks

```bash
celery -A celery_worker.celery call send_daily_reminders
celery -A celery_worker.celery call send_monthly_report
```

---

## 🚀 Running the Application

### Start Backend APIs

```bash
cd backend
python run.py
```

### Start Frontend (Vue.js)

```bash
cd frontend
npm install     # only once to install dependencies
npm run serve   # start frontend server
```

---

## ✅ Summary

| Component      | Command or Info                          |
| -------------- | ---------------------------------------- |
| Backend API    | `python run.py` (inside `backend/`)      |
| Frontend (Vue) | `npm run serve` (inside `frontend/`)     |
| Redis Server   | `redis-server` (via WSL/Linux)           |
| Celery Worker  | `celery -A celery_worker.celery worker`  |
| Flask Shell    | `flask shell` → use admin creation/query |