# Batcomputer AI Assistant

A powerful, Batman-themed AI personal assistant powered by Google Gemini, Spotify, and system-level integrations.

## 🦇 Features

- **Voice & Terminal Interface**: Control your system using voice commands (Push-to-Talk with 'Shift') or via the terminal.
- **AI Intelligence**: Powered by Google Gemini 1.5 Flash for natural conversations and screen analysis.
- **Visual Intel**: Generate high-quality images using Google Imagen 3.0.
- **Spotify Integration**: Full control over your music—play specific tracks, pause, skip, and adjust volume.
- **Vision Link**: Capture and analyze your current screen content for tactical summaries.
- **System Controls**:
  - Adjust system volume and brightness.
  - Search and open files/folders globally.
  - Launch applications (Chrome, WhatsApp, Games, etc.).
- **Weather Updates**: Real-time weather information at your location.

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- A Google Gemini API Key
- Spotify Premium (for API playback control)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Nihar-saw/ai-assistant.git
   cd ai-assistant
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: Ensure you have `edge-tts`, `pygame`, `spotipy`, `google-generativeai`, `psutil`, `screen-brightness-control`, `pycaw`, `comtypes`, and `keyboard` installed.)*

3. Set up environment variables:
   - `GEMINI_API_KEY`: Your Google Gemini API key.

### Configuration

- **Spotify**: Update `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`, and `SPOTIPY_REDIRECT_URI` in `main.py` with your Spotify Developer credentials.
- **App Mappings**: Add your local application paths in `apps.py`.

## 🛠️ Usage

Run the main script:
```bash
python main.py
```

- **Hold `SHIFT`**: Activate voice listening.
- **Terminal**: Type commands directly into the prompt.

### Example Commands

- "Generate an image of a futuristic Gotham City."
- "Play Dark Knight soundtrack on Spotify."
- "Look at my screen and tell me what you see."
- "Open WhatsApp."
- "What's the weather like?"
- "Set system volume to 50%."

## 📜 License

This project is open-source. Use it to protect your city.