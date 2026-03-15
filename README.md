# Attendance Tracker (Django)

[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen)](https://attendance-tarcker.onrender.com)

A simple class attendance tracker built with Django, including responsive dashboard, course management, and attendance reporting.

## ✅ Features
- User signup/login/authentication
- Create and manage courses
- Mark attendance (Present/Absent/Holiday)
- Dashboard with overall, monthly, weekly attendance analytics and charts
- Profile avatar upload and selection
- Responsive UI for desktop/mobile
- Ready-to-deploy to Render with Gunicorn and WhiteNoise

## 📁 Project Structure
- `attendance_tracker/` — Django project settings, URLs, WSGI
- `tracker/` — Django app (models, views, templates, static files)
- `db.sqlite3` — local SQLite database
- `Procfile` — Render startup command
- `requirements.txt` — Python dependencies
- `runtime.txt` — Python runtime for Render

## ⚙️ Local Setup
1. Clone repository:
   ```bash
   git clone (https://github.com/kunalSingh026/Attendance-Tarcker.git)
   cd attendance_tracker
   ```
2. Create and activate venv:
   ```bash
   python -m venv env
   .\env\Scripts\activate    # Windows
   source env/bin/activate     # macOS/Linux
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run migrations:
   ```bash
   python manage.py migrate
   ```
5. Create superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```
6. Start server:
   ```bash
   python manage.py runserver
   ```
7. Open:
   - `http://127.0.0.1:8000/`

## 🌐 Deploy (Render)
This app is configured for Render deployment.

1. Ensure these files exist:
   - `Procfile`
   - `requirements.txt`
   - `runtime.txt`
2. In `settings.py`:
   - `DEBUG=False` in production
   - `ALLOWED_HOSTS` includes Render host
3. `Procfile` command runs migrations and starts Gunicorn:
   ```procfile
   web: sh -lc "python manage.py collectstatic --noinput && python manage.py migrate && gunicorn attendance_tracker.wsgi:application"
   ```
4. Push to GitHub; Render auto-deploy from branch.

## 📝 App Usage
- Visit `/signup/` to create an account
- Add courses at `/courses/`
- Mark attendance at `/track/`
- See analytics at `/dashboard/`

## 🧪 How to Test Quickly
1. Start local server:
   ```bash
   python manage.py runserver
   ```
2. Register a test account or use an existing user.
3. Create one course and mark attendance for today.
4. Visit `/dashboard/` and verify charts/tables update.

### Quick production check
Run these commands for Render logs and health:
```bash
python manage.py collectstatic --noinput
python manage.py migrate
# If using Render CLI:
# render logs <service-name>
```

## 🛠️ Troubleshooting
- If you see `500` in production, check Render logs for static file or DB migrations.
- Ensure database migrations run before gunicorn.
- Add `RENDER_EXTERNAL_HOSTNAME` host to `ALLOWED_HOSTS` in production settings.

## ✅ Quick Commands
```bash
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn attendance_tracker.wsgi:application
```

## 💡 Notes
- For production, use a dedicated DB (Postgres) and secure `SECRET_KEY` in environment variables.
- Keep `DEBUG=False` in production.

## 🚀 Next Improvements
These are useful future upgrades if you want to extend this app:
- Add CSV import/export for attendance records.
- Add role-based access (students vs teachers).
- Add email reminders for low attendance.
- Add API endpoints for mobile frontend / integrations.
- Add unit tests for views/models and CI checks.

---

Built by Kunal.
