#!/usr/bin/env python3

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Transcribe large
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
from pydub import AudioSegment
import tempfile
import math

# Load Environment Variables
from dotenv import load_dotenv
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Supported file extensions
SUPPORTED_AUDIO = ['.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm']
SUPPORTED_VIDEO = ['.mp4', '.mpeg', '.mpg', '.avi', '.mov', '.flv', '.wmv']

MAX_FILE_SIZE = 24 * 1024 * 1024  # 24 MB in bytes (leaving some margin)

def is_supported_file(file_path):
    extension = Path(file_path).suffix.lower()
    return extension in SUPPORTED_AUDIO or extension in SUPPORTED_VIDEO

def split_audio(file_path, max_size_mb=24):
    print(f"Splitting audio file: {file_path}")
    audio = AudioSegment.from_file(file_path)
    max_size_bytes = max_size_mb * 1024 * 1024
    duration_ms = len(audio)
    chunk_duration_ms = math.floor((max_size_bytes / len(audio.raw_data)) * duration_ms)
    
    chunks = []
    for i in range(0, duration_ms, chunk_duration_ms):
        print(f"Creating chunk from {i}ms to {i+chunk_duration_ms}ms")
        chunk = audio[i:i+chunk_duration_ms]
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            chunk.export(temp_file.name, format="mp3", bitrate="128k")
            chunk_size = os.path.getsize(temp_file.name)
            print(f"Chunk size: {chunk_size / 1024 / 1024:.2f} MB")
            chunks.append(temp_file.name)
    
    return chunks

def transcribe_chunk(file_path):
    try:
        file_size = os.path.getsize(file_path)
        print(f"Transcribing chunk: {file_path}, Size: {file_size / 1024 / 1024:.2f} MB")
        with open(file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return transcript.text
    except Exception as e:
        return f"Error during transcription: {str(e)}"

def transcribe_media(file_path):
    file_size = os.path.getsize(file_path)
    print(f"File size: {file_size / 1024 / 1024:.2f} MB")
    if file_size <= MAX_FILE_SIZE:
        return transcribe_chunk(file_path)
    else:
        print("File is too large. Splitting into chunks...")
        chunks = split_audio(file_path)
        transcripts = []
        for i, chunk in enumerate(chunks):
            print(f"Transcribing chunk {i+1} of {len(chunks)}...")
            transcripts.append(transcribe_chunk(chunk))
            os.unlink(chunk)  # Delete the temporary file
        return " ".join(transcripts)

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