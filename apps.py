# apps.py
import subprocess
import os
import webbrowser

APP_MAP = {
    'hollow knight': r"C:\Games\Hollow Knight\hollow_knight.exe",
    'chrome': r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    'youtube': "https://www.youtube.com",
    'whatsapp': r"C:\Users\Nihar\AppData\Local\WhatsApp\WhatsApp.exe"
}

def launch_app(app_name):
    app_name = app_name.lower()
    if app_name in APP_MAP:
        target = APP_MAP[app_name]
        if target.startswith("http"):
            webbrowser.open(target)
            return f"Opening {app_name} in your browser."
        elif os.path.exists(target):
            subprocess.Popen(target)
            return f"Launching {app_name} now."
        else:
            return f"Path for {app_name} not found."
    return None # Return None if not found to let the main script try other searches
