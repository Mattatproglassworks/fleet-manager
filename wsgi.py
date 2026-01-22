"""
PythonAnywhere WSGI Configuration File

INSTRUCTIONS:
1. Go to PythonAnywhere.com and create an account
2. Open a Bash console and run:
   git clone https://github.com/Mattatproglassworks/fleet-manager.git
   cd fleet-manager
   mkvirtualenv --python=/usr/bin/python3.10 fleet-env
   pip install -r requirements.txt
   python migrate_security.py
   python create_user.py

3. Go to Web tab → Add new web app → Manual configuration → Python 3.10
4. Click on "WSGI configuration file" link
5. Replace ALL content with the code below (update YOUR_USERNAME)
"""

# ============ COPY BELOW THIS LINE INTO PYTHONANYWHERE WSGI FILE ============

import sys
import os

# CHANGE 'YOUR_USERNAME' to your PythonAnywhere username
project_path = '/home/YOUR_USERNAME/fleet-manager'

if project_path not in sys.path:
    sys.path.insert(0, project_path)

# Set production environment variables
os.environ['SECRET_KEY'] = '0f2ed3ae5105f1cad555fb9b7f0d3743a7b0192f916d7231e00bfc97196ca8df'
os.environ['FLASK_ENV'] = 'production'

from app import app as application

# ============ COPY ABOVE THIS LINE INTO PYTHONANYWHERE WSGI FILE ============
