# 🚀 Quick Deployment Guide - Fleet Management System

## Option 1: Deploy to PythonAnywhere (Recommended - Free!)

### Pre-Deployment Checklist
- [x] Security features implemented
- [x] Login system bulletproofed
- [x] Profile management working
- [x] Bootstrap icons fixed
- [ ] Set SECRET_KEY in .env file
- [ ] Create admin user

### Step-by-Step Deployment

#### 1. Create PythonAnywhere Account
- Go to https://www.pythonanywhere.com
- Sign up for FREE account
- Verify email

#### 2. Upload Files (Choose one method)

**Method A: Direct Upload**
1. Go to Files tab
2. Create directory: `fleet-manager`
3. Upload all files except:
   - `instance/` folder (database will be created fresh)
   - `__pycache__/`
   - `.env` (create new on server)

**Method B: Git (Recommended)**
```bash
# On your local machine (in this folder):
git init
git add .
git commit -m "Initial commit - Fleet Manager v2.0"
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main

# On PythonAnywhere Bash console:
git clone YOUR_GITHUB_REPO_URL fleet-manager
```

#### 3. Set Up Virtual Environment
```bash
cd ~
mkvirtualenv --python=/usr/bin/python3.10 fleetenv
cd fleet-manager
pip install -r requirements.txt
```

#### 4. Create .env File
```bash
cd ~/fleet-manager
nano .env
```

Add this content:
```
SECRET_KEY=YOUR_GENERATED_SECRET_KEY_HERE
SESSION_LIFETIME_DAYS=30
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=15
```

Generate SECRET_KEY:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

#### 5. Initialize Database
```bash
cd ~/fleet-manager
python3 << EOF
from app import app, db
with app.app_context():
    db.create_all()
    print("✅ Database created!")
EOF
```

#### 6. Create Admin User
```bash
python3 create_user.py
```
Follow prompts to create your admin account.

#### 7. Configure Web App

**A. Create Web App**
- Go to Web tab → Add new web app
- Choose Manual configuration
- Python 3.10

**B. Configure WSGI**
Click WSGI config file, replace all content:
```python
import sys
import os

# Add your project directory
path = '/home/YOUR_USERNAME/fleet-manager'
if path not in sys.path:
    sys.path.append(path)

# Load environment variables
from dotenv import load_dotenv
project_folder = os.path.expanduser('~/fleet-manager')
load_dotenv(os.path.join(project_folder, '.env'))

# Import Flask app
from app import app as application
```

**C. Set Virtual Environment**
Virtualenv: `/home/YOUR_USERNAME/.virtualenvs/fleetenv`

**D. Configure Static Files**
URL: `/static/`
Directory: `/home/YOUR_USERNAME/fleet-manager/static`

#### 8. Reload & Launch
- Click green "Reload" button
- Visit: `https://YOUR_USERNAME.pythonanywhere.com`

---

## Option 2: Deploy to Heroku

### Prerequisites
- Heroku account
- Heroku CLI installed

### Quick Deploy
```bash
# Login to Heroku
heroku login

# Create app
heroku create your-fleet-manager

# Add PostgreSQL (optional, SQLite works too)
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
heroku config:set FLASK_ENV=production

# Create Procfile
echo "web: gunicorn app:app" > Procfile

# Add gunicorn to requirements.txt
echo "gunicorn==21.2.0" >> requirements.txt

# Deploy
git init
git add .
git commit -m "Deploy to Heroku"
git push heroku main

# Initialize database
heroku run python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Create admin user
heroku run python create_user.py

# Open app
heroku open
```

---

## Option 3: Deploy to Railway.app

### Quick Deploy
1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Add environment variables:
   - `SECRET_KEY`: Generate with Python
   - `PORT`: 5000
6. Railway auto-detects Flask and deploys!

---

## Post-Deployment Checklist

After deploying:
- [ ] Test login with admin account
- [ ] Change admin password
- [ ] Test adding a vehicle
- [ ] Test adding maintenance record
- [ ] Test profile updates
- [ ] Test username/email changes
- [ ] Test password change
- [ ] Verify failed login lockout works
- [ ] Check all icons display correctly
- [ ] Test on mobile device

---

## Security Notes for Production

⚠️ **IMPORTANT**: Before going live:

1. **SECRET_KEY**: Must be set in .env (never hardcode)
2. **Debug Mode**: Ensure `debug=False` in production
3. **HTTPS**: Use HTTPS (PythonAnywhere provides this free)
4. **Database Backups**: Set up regular backups
5. **Monitor Logs**: Check error logs regularly

---

## Troubleshooting

### Issue: "ImportError: No module named 'app'"
**Fix**: Check WSGI path matches your username

### Issue: "Static files not loading"
**Fix**: Verify static files path in Web tab

### Issue: "500 Internal Server Error"
**Fix**: Check error logs in Web tab → Log files

### Issue: "Database locked"
**Fix**: SQLite doesn't handle multiple workers well
- For PythonAnywhere free tier, this shouldn't be an issue
- For production with traffic, consider PostgreSQL

---

## Need Help?

- PythonAnywhere Help: https://help.pythonanywhere.com
- Flask Deployment: https://flask.palletsprojects.com/en/latest/deploying/
- Security Docs: See SECURITY.md in this repository

---

**Last Updated**: January 21, 2026
**Version**: 2.0 with Security Features
