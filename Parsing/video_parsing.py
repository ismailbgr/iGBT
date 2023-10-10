'''
This script convert given mp4 video to mp3 audio file.

'''
import subprocess

def pars(input_file, output_file):
    """
    Converts a given mp4 video file to an mp3 audio file.

    Args:
        input_file (str): The path to the input mp4 video file.
        output_file (str): The desired path for the output mp3 audio file.
    """
    # Construct the FFmpeg command
    command = [
    "ffmpeg",
    "-i", input_file,
    "-vn",
    "-acodec", "libmp3lame",
    "-q:a", "4",
    "-y",
    output_file
    ]
    # Run the FFmpeg command
    subprocess.run(command, check=True)
    print(f"Conversion completed. Output file: {output_file}")
