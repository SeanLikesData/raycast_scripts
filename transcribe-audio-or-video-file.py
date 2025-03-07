#!/usr/bin/env python3

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Transcribe Audio/Video
# @raycast.mode compact

# Optional parameters:
# @raycast.icon 🎙️
# @raycast.argument1 { "type": "text", "placeholder": "Path to audio/video file" }
# @raycast.packageName Media Tools

# Documentation:
# @raycast.description Transcribe audio or video file using OpenAI's Whisper model
# @raycast.author Sean Knight
# @raycast.authorURL https://github.com/seanlikesdata

import sys
import os
from openai import OpenAI
from pathlib import Path
## Load Environment Variables
from dotenv import load_dotenv
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Supported file extensions
SUPPORTED_AUDIO = ['.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm']
SUPPORTED_VIDEO = ['.mp4', '.mpeg', '.mpg', '.avi', '.mov', '.flv', '.wmv']

def is_supported_file(file_path):
    extension = Path(file_path).suffix.lower()
    return extension in SUPPORTED_AUDIO or extension in SUPPORTED_VIDEO

def transcribe_media(file_path):
    try:
        with open(file_path, "rb") as media_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=media_file
            )
        return transcript.text
    except Exception as e:
        return f"Error during transcription: {str(e)}"

def main():
    if len(sys.argv) < 2:
        print("Please provide the path to the audio or video file.")
        return

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    if not is_supported_file(file_path):
        print(f"Unsupported file type. Supported types are: {', '.join(SUPPORTED_AUDIO + SUPPORTED_VIDEO)}")
        return

    print("Transcribing... This may take a while depending on the file size.")

    transcript = transcribe_media(file_path)
    
    # Save transcript to a file in the same directory as the input file
    file_dir = os.path.dirname(file_path)
    file_name = Path(file_path).stem
    transcript_path = os.path.join(file_dir, f"{file_name}_transcript.txt")
    
    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(transcript)
    
    print(f"Transcription saved to: {transcript_path}")

if __name__ == "__main__":
    main()
    
