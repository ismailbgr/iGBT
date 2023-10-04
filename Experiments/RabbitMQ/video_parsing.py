'''
This script convert given mp4 video to mp3 audio file.

'''
import subprocess
def pars(input_file, output_file):
    # Construct the FFmpeg command
    command = [
    "ffmpeg",
    "-i", input_file,
    "-vn",
    "-acodec", "libmp3lame",
    "-q:a", "4",
    output_file
    ]
    # Run the FFmpeg command
    subprocess.run(command)
    print(f"Conversion completed. Output file: {output_file}")
