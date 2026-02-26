import threading
import time
import os
import re
import asyncio
import sys
import subprocess
import fnmatch
from datetime import datetime
from io import BytesIO
import PIL.Image
from PIL import ImageGrab
import webbrowser
import speech_recognition as sr
import keyboard
import requests
import pygame
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import google.generativeai as genai
import psutil
import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# External mapping files
import apps # Ensure apps.py exists with launch_app() function

# --- Config & AI Setup ---
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyABhfNpx1VOO_eHnKDq9cRf95R1mZXy9Xo")
genai.configure(api_key=GEMINI_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')
chat_session = model.start_chat(history=[])

# --- Spotify Setup ---
SPOTIPY_CLIENT_ID = ''
SPOTIPY_CLIENT_SECRET = ''
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:8888/callback'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope="user-modify-playback-state user-read-playback-state"
))

# --- Speech Engine ---
pygame.mixer.init()
VOICE = "en-US-ChristopherNeural"

def speak(text, block=True):
    print(f"\n[BATCOMPUTER] {text}")
    async def _generate():
        import edge_tts
        await edge_tts.Communicate(text, VOICE).save("temp_speech.mp3")
    try:
        asyncio.run(_generate())
        pygame.mixer.music.load("temp_speech.mp3")
        pygame.mixer.music.play()
        if block:
            while pygame.mixer.music.get_busy(): time.sleep(0.1)
            pygame.mixer.music.unload()
            try: os.remove("temp_speech.mp3")
            except: pass
    except Exception as e: print(f"Voice Error: {e}")

# --- Core Logic Functions ---

def generate_visual_intel(prompt):
    speak(f"Initializing neural canvas for: {prompt}")
    try:
        img_model = genai.GenerativeModel('imagen-3.0-generate-001')
        response = img_model.generate_content(prompt)
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'inline_data'):
                img = PIL.Image.open(BytesIO(part.inline_data.data))
                filename = f"intel_{int(time.time())}.png"
                img.save(filename)
                os.startfile(filename)
                return f"Visual intelligence saved as {filename}."
    except Exception as e:
        return f"Image generation failed: {e}"

def get_weather():
    url = "https://api.open-meteo.com/v1/forecast?latitude=19.4174&longitude=72.8197&current_weather=true"
    try:
        temp = requests.get(url).json()['current_weather']['temperature']
        return f"It is currently {temp} degrees Celsius."
    except: return "Weather satellites unreachable."

def set_system_volume(level):
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        
        volume.SetMasterVolumeLevelScalar(level / 100, None)
        return True
    except Exception as e:
        print(f"System Volume Error: {e}")
        return False

def find_item_globally(name):
    speak(f"Scanning sectors for {name}...")
    search_paths = [os.path.expanduser("~/Desktop"), os.path.expanduser("~/Documents"), os.path.expanduser("~/Downloads")]
    for path in search_paths:
        for root, dirs, files in os.walk(path, topdown=True):
            try:
                for dirname in dirs:
                    if name.lower() in dirname.lower():
                        full_path = os.path.join(root, dirname)
                        os.startfile(full_path)
                        return f"Directory {dirname} accessed."
                for filename in files:
                    if name.lower() in filename.lower():
                        full_path = os.path.join(root, filename)
                        os.startfile(full_path)
                        return f"File {filename} accessed."
            except PermissionError: continue 
    return "No accessible matches found."

def play_spotify(query):
    try:
        devices = sp.devices()
        # Find if any device is actually active
        active_devices = [d for d in devices['devices'] if d['is_active']]
        
        if not active_devices:
            speak("No active device detected. Please open Spotify on your terminal.")
            # Optional: Try to force open the app
            os.startfile("spotify.exe") 
            return

        results = sp.search(q=query, limit=1, type='track')
        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            # Use the first active device ID specifically
            device_id = active_devices[0]['id']
            sp.start_playback(device_id=device_id, uris=[track['uri']])
            speak(f"Playing {track['name']} on {active_devices[0]['name']}.")
    except Exception as e:
        if "403" in str(e):
            speak("Access denied. Ensure you have an active Premium session and Spotify is not playing an ad.")
        else:
            speak("Spotify uplink failed.")

# --- Main Command Processor ---
def process_command(cmd):
    cmd = cmd.lower().strip()
    if not cmd: return

    # 1. System Controls
    if any(x in cmd for x in ("exit", "quit", "shutdown")):
        speak("Powering down systems. Goodbye.")
        os._exit(0)

    # 2. Visual Intelligence
    if any(x in cmd for x in ("generate image", "visualize", "create image")):
        prompt = cmd.replace("generate image", "").replace("visualize", "").replace("create image", "").strip()
        if prompt:
            threading.Thread(target=lambda: speak(generate_visual_intel(prompt))).start()
        else: speak("Please provide a description.")
        return

    # 3. Media Controls
    if "play " in cmd:
        query = cmd.replace("play ", "").strip()
        try:
            results = sp.search(q=query, limit=10, type='track')
            if results['tracks']['items']:
                t = results['tracks']['items'][0]
                print(f"Playing: {t['name']} by {t['artists'][0]['name']}")
                sp.start_playback(uris=[t['uri']])
            else: speak("Track not found.")
        except Exception as e: speak("Spotify playback failed.")
        return

    if "pause" in cmd:
        try: sp.pause_playback(); speak("Paused.")
        except: speak("Command failed.")
        return

    if "resume" in cmd or "play" in cmd:
        try: sp.start_playback(); speak("Resuming.")
        except: speak("Command failed.")
        return

    if "skip" in cmd or "next" in cmd:
        try: sp.next_track(); speak("Skipping to next track.")
        except: speak("Command failed.")
        return

    if "previous" in cmd or "back" in cmd:
        try: sp.previous_track(); speak("Going back to previous track.")
        except: speak("Command failed.")
        return

    if "volume" in cmd:
        match = re.search(r"(\d{1,3})",cmd)

        if "mute" in cmd or "zero" in cmd:
            target_volume=0
        elif "max" in cmd or "full" in cmd:
            target_volume=100
        elif match:
            target_volume=int(match.group(1))
    
        else:
            target_volume=None
        
        if target_volume is not None:
            if 0 <= target_volume <= 100:
                try:
                    sp.volume(target_volume)
                    speak(f"Volume set to {target_volume} percent.")
                except Exception as e:
                    speak(f"Volume adjustment failed: {e}")
            else:
                speak("Please specify a volume between 0 and 100.")
        return
    
    if "autoplay " in cmd:
        query = cmd.replace("autoplay ", "").strip()
        threading.Thread(target=lambda: speak(play_with_autoplay(query))).start()
        return
    
    if "system volume" in cmd:
        match = re.search(r"(\d{1,3})", cmd)
        if match:
            level = int(match.group(1))
            if 0 <= level <= 100:
                if set_system_volume(level):
                    speak(f"Master audio adjusted to {level} percent.")
                else:
                    speak("I am unable to access the audio hardware.")
            else:
                speak("Volume must be between 0 and 100.")
        return

    if "mute system" in cmd:
        if set_system_volume(0):
            speak("Master audio muted.")
        else:
            speak("I am unable to access the audio hardware.")
        return
        
    # 4. Utilities
    if "brightness" in cmd:
        match = re.search(r"(\d{1,3})", cmd)
        level = 100 if any(x in cmd for x in ("max", "full")) else (int(match.group(1)) if match else None)
        if level is not None:
            try: sbc.set_brightness(level); speak(f"Brightness {level} percent.")
            except: speak("Hardware error.")
        return

    if any(x in cmd for x in ("find", "locate", "search")):
        target = cmd.replace("find", "").replace("locate", "").replace("search", "").strip()
        if target: threading.Thread(target=lambda: speak(find_item_globally(target))).start()
        return

    if "weather" in cmd:
        speak(get_weather())
        return

    if "open " in cmd:
        app_name = cmd.replace("open ", "").strip()
        speak(apps.launch_app(app_name))
        return

    # 5. Vision & Chat
    if "look at my screen" in cmd:
        speak("Analyzing display...")
        screenshot = ImageGrab.grab()
        try:
            response = chat_session.send_message(["Tactical summary of this screen.", screenshot])
            speak(response.text)
        except: speak("Vision link failed.")
        return
    
    if "open" in cmd or "launch" in cmd:
        app_name = cmd.replace("open", "").replace("launch", "").strip()
        speak(apps.launch_app(app_name))
        return

        if result:
            speak(result)
        else:
            speak(f"No direct match for {app_name}. Attempting global search.")
            threading.Thread(target=lambda: speak(find_item_globally(app_name))).start()
        return

    # Default Chat
    try:
        response = chat_session.send_message(cmd)
        speak(response.text.replace("*", ""))
    except: speak("Uplink failed.")

# --- Assistant Runner ---
class Assistant:
    def __init__(self, push_key="shift"):
        self.recognizer, self.mic = sr.Recognizer(), sr.Microphone()
        self.push_key = push_key
        self.running = True

    def listen_voice(self):
        speak("Awaiting instructions.")
        with self.mic as source:
            try:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
                text = self.recognizer.recognize_google(audio)
                print(f"[VOICE]: {text}")
                process_command(text)
            except: print("[ERROR]: Voice not recognized.")

    def keyboard_loop(self):
        while self.running:
            if keyboard.is_pressed(self.push_key):
                self.listen_voice()
                time.sleep(0.5)
            time.sleep(0.01)

    def run(self):
        threading.Thread(target=self.keyboard_loop, daemon=True).start()
        print(f"--- SYSTEMS ACTIVE ---\nHold '{self.push_key.upper()}' to talk")
        while self.running:
            try:
                cmd = input("Terminal > ").strip()
                process_command(cmd)
            except EOFError: break

if __name__ == "__main__":
    Assistant().run()
