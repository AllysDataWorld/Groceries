# Migration from Windows to Linux (Raspberry Pi4000 with built-in Keyboard)

## I have a Flask + SQLITE project on a windows computer, and now I want to move it to a raspberry pi. 
### git repo onto the pi
sudo apt-get update
sudo apt-get install git-all
git version 
-   installed git version 2.39.5

###### do not use git init
git clone https://github.com/AllysDataWorld/Groceries.git


# Steps to setup App on Raspberry Pi:



### ModelB Pi4000 is running the OS: Debian GNU/Linux 12 bookworm
- My computer is running Python 3.12.12, and the current Pi version of Python is 3.9 which causes syntax issues while running the flask code
- Bookworm's is running Python 3.11.2


# Set up a Python virtual environment: Create and Activate:
- `cd ~/Groceries`
- `python3 -m venv AI`
- `source AI/bin/activate` 


# INSTALL PACKAGES

## **Prep on Windows computer dependencies**
- pip freeze > requirements.txt
  
## **Install dependencies**

## INSIDE VIRUAL ENVIRONMENT:
- On Pi target computer: 
- pip install --upgrade pip
  >>Successfully installed pip-26.0.1
    - Go to Python Terminal:

   > `>>> from install import clean_requirements`
   > `>>>clean_requirements()`

- python3 -m pip install -r requirements_clean.txt

- ensure that all the packages are installed:
    > from install import clean_requirements()
    > clean_requirements()

## **THEN install pytesseract**: _first install dependents_:
sudo apt install -y libjpeg-dev zlib1g-dev libpng-dev libfreetype6-dev libwebp-dev libtiff-dev libtiff5
sudo apt install -y tesseract-ocr-eng
pip install pytesseract
pip install flask
pip install flask_sqlalchemy
pip install flask_migrate
pip install pytz
pip install python-dateutil
pip install pandas==2.3.3

    Successfully installed Pillow-12.2.0 packaging-26.0 pytesseract-0.3.13
    Successfully installed blinker-1.9.0 click-8.3.2 flask-3.1.3 itsdangerous-2.2.0 jinja2-3.1.6 markupsafe-3.0.3 werkzeug-3.1.8
    Successfully installed flask_sqlalchemy-3.1.1 greenlet-3.3.2 sqlalchemy-2.0.49 typing-extensions-4.15.0
    Successfully installed Mako-1.3.10 alembic-1.18.4 flask_migrate-4.1.0
    Successfully installed pytz-2026.1.post1


- VERIFY Pillow:
python - << 'EOF' #This means go into python until I type 'EOF'
from PIL import Imager
print("Pillow OK:", Image)
EOF


**Create all the folders that are needed**:
   > from install import MAKE_FOLDERS, create_app_folders
   > from outside the Groceries folder run: create_app_folders(MAKE_FOLDERS)

3. SQLite database - Create a Fresh database
   > `flask shell`
   > > db.create_all()`

4. Place the CSV in the output folder:
Distinct_Grocery_Items.CSV <---

# Test it runs
flask run --host=0.0.0.0 --port=5000
--host=0.0.0.0 makes it accessible from other devices on the network, not just localhost.

# THEN test it runs
python run.py



### NOTE to keep in mind: 
> app.secret_key = secrets.token_hex(16)
- What does secret_key protect?
It's used to cryptographically sign Flask sessions — the cookie stored in the user's browser that tracks things like login state or flash messages. 
- Without it, users could forge or tamper with their own session cookie.
- The catch with your current approach: secrets.token_hex(16) generates a new random key every time the app starts. 
  - This means:
  - Every time you restart Flask, all existing sessions are invalidated
  - Any user who was "logged in" gets logged out
  - Flash messages in-flight get lost

- For a personal Pi app this is fine.
- For your use case — no login, local network only, just you and your wife — it doesn't matter. A random key on each restart is perfectly fine.
The secret key mainly matters for:
- Login sessions — you have none
- "Remember me" cookies — not applicable
- Flash messages — these would just disappear on restart, which is a minor annoyance at worst

- The only realistic scenario where it'd affect you is if Flask restarts mid-use (e.g. after a Pi reboot) and a flash message like "Receipt uploaded successfully" disappears. That's harmless.
- So your current code is fine as-is for a local family app.

  - But if you want sessions to survive restarts, use a fixed key instead:
  pythonapp.secret_key = 'some-fixed-secret-string'
  Or load it from a config file/env var so it's not hardcoded in source.
  Do you need to share the same key between your Windows dev machine and the Pi? No — they're separate running instances, sessions from one won't transfer to the other anyway.



# (Optional but recommended) Run it properly with Gunicorn
The Flask dev server isn't meant for real use. Install Gunicorn:

bash
pip install gunicorn
gunicorn -w 2 -b 0.0.0.0:5000 app:app
Replace app:app with module_name:flask_app_variable.

7. (Optional) Auto-start on boot with systemd
Create /etc/systemd/system/myapp.service:

ini
[Unit]
Description=My Flask App
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/your-project
Environment="PATH=/home/pi/your-project/venv/bin"
ExecStart=/home/pi/your-project/venv/bin/gunicorn -w 2 -b 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
Then enable it:

bash
sudo systemctl daemon-reload
sudo systemctl enable myapp
sudo systemctl start myapp
Common Pi-specific gotchas:

Some Python packages with C extensions (e.g. cryptography, Pillow) need to be compiled for ARM — they may take a while to install or require apt dependencies like libffi-dev or libjpeg-dev
SQLite write permissions — make sure the pi user owns the .db file and its directory
If you're on Pi OS Bookworm (2023+), use --break-system-packages or a venv (venv is the better path, which you're already doing)