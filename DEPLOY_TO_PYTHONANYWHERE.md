# PythonAnywhere Deployment Guide for Fleet Manager

## Step 1: Create a PythonAnywhere Account
1. Go to https://www.pythonanywhere.com
2. Click "Start running Python online" and sign up for a **free Beginner account**
3. Verify your email

## Step 2: Upload Your Files
1. Log in to PythonAnywhere
2. Go to the **Files** tab
3. Create a new directory called `fleet-management`
4. Upload ALL files from your local `fleet-management` folder:
   - app.py
   - models.py
   - document_processor.py
   - requirements.txt
   - templates/ (entire folder)
   - static/ (entire folder)

**Tip:** You can also use the "Open Bash console" and git clone if you put your code on GitHub.

## Step 3: Set Up Virtual Environment
1. Go to the **Consoles** tab
2. Start a new **Bash** console
3. Run these commands:

```bash
cd ~
mkvirtualenv --python=/usr/bin/python3.10 fleetenv
pip install -r fleet-management/requirements.txt
```

## Step 4: Create the Web App
1. Go to the **Web** tab
2. Click **Add a new web app**
3. Choose **Manual configuration** (not Flask!)
4. Select **Python 3.10**

## Step 5: Configure WSGI
1. In the Web tab, click on the **WSGI configuration file** link
2. Delete everything and replace with:

```python
import sys
path = '/home/YOUR_USERNAME/fleet-management'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```

**Replace YOUR_USERNAME with your PythonAnywhere username!**

## Step 6: Configure Virtual Environment
1. In the Web tab, find **Virtualenv** section
2. Enter: `/home/YOUR_USERNAME/.virtualenvs/fleetenv`

## Step 7: Configure Static Files
1. In the Web tab, find **Static files** section
2. Add:
   - URL: `/static/`
   - Directory: `/home/YOUR_USERNAME/fleet-management/static`

## Step 8: Update app.py for Production
The app needs a small change. In PythonAnywhere Bash console:

```bash
cd ~/fleet-management
nano app.py
```

Find the line at the bottom that says:
```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

Change `debug=True` to `debug=False` for production.

## Step 9: Initialize Database
In the Bash console:
```bash
cd ~/fleet-management
python -c "from app import db, app; app.app_context().push(); db.create_all()"
```

## Step 10: Reload and Launch!
1. Go back to the **Web** tab
2. Click the green **Reload** button
3. Click your web app URL (it will be: `YOUR_USERNAME.pythonanywhere.com`)

## Your App is Now Live! 🎉

You can access it from anywhere at:
**https://YOUR_USERNAME.pythonanywhere.com**

---

## Troubleshooting

### If you see an error:
1. Go to Web tab → Error log
2. Check what went wrong

### Common issues:
- **ModuleNotFoundError**: Make sure virtualenv path is correct
- **Template not found**: Check that templates folder was uploaded
- **Database error**: Run the database initialization command again

### To update your app later:
1. Upload new files via Files tab
2. Click Reload in Web tab

