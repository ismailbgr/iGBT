'''
This script convert given mp4 video to mp3 audio file.

'''
import subprocess
from celery import Celery
import base64
import uuid

app = Celery('videoparser', broker='amqp://localhost:5672', backend='redis://localhost:6379/0')

@app.task
def pars(input_file):
    """
    Converts a given mp4 video file to an mp3 audio file.

    Args:
        input_file (str): The path to the input mp4 video file.
    """
    uuidname = str(uuid.uuid4())
    with open(f'/tmp/{uuidname}.mp4', 'wb') as f:
        f.write(base64.b64decode(input_file))
    input_file = f'/tmp/{uuidname}.mp4'
    output_file = f'/tmp/{uuidname}.mp3'

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
    
    with open(output_file, 'rb') as f:
        data = f.read()
        b64 = base64.b64encode(data)
    return b64

