#!/usr/bin/env python3

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Convert Video to MP3
# @raycast.mode silent

# Optional parameters:
# @raycast.icon 🎵
# @raycast.argument1 { "type": "text", "placeholder": "Video file path" }

# Documentation:
# @raycast.description Convert a video file to MP3 audio
# @raycast.author Sean Knight
# @raycast.authorURL https://github.com/seanlikesdata

# / Workflow: On a mac, right click on the target file, then hold down the option key and select "Copy <filename> as Pathname"
# / Then, run the script with the copied path as the argument

import sys
import os
import subprocess

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        return False

def convert_to_mp3(input_file):
    if not check_ffmpeg():
        print("FFmpeg is not installed. Please install it using 'brew install ffmpeg'")
        sys.exit(1)

    # Expand user directory if path starts with ~
    input_file = os.path.expanduser(input_file)
    
    # Resolve the full path
    input_file = os.path.abspath(input_file)
    
    # Check if the input file exists
    if not os.path.exists(input_file):
        print(f"Error: The file '{input_file}' does not exist.")
        sys.exit(1)

    output_file = os.path.splitext(input_file)[0] + '.mp3'
    
    try:
        subprocess.run([
            "ffmpeg",
            "-i", input_file,
            "-vn",
            "-acodec", "libmp3lame",
            "-b:a", "192k",
            output_file
        ], check=True, stderr=subprocess.PIPE)
        print(f"Successfully converted {os.path.basename(input_file)} to {os.path.basename(output_file)}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e.stderr.decode()}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <input_video_path>")
        sys.exit(1)
    
    convert_to_mp3(sys.argv[1])