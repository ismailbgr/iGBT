import subprocess
from celery import Celery, current_task, states
import base64
import uuid
import yaml
from Downloader import YouTubeDownloader
import os

# Load config
config = None
with open("/app/config/config.yml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

print("config: ", config)

# Create the Celery app

app = Celery(
    "videoparser",
    broker=config["celery"]["broker"],
    backend=config["celery"]["backend"],
)

app.conf.task_routes = {
    "convert_video_to_mp3": {"queue": "videoparser"},
    "youtube_dl": {"queue": "videoparser"},
}


@app.task(name="convert_video_to_mp3")
def convert_video_to_mp3(input_filepath):
    """
    Converts a given mp4 video file to an mp3 audio file.

    Args:
        input_file (str): The path to the input mp4 video file.

    Returns:
        str: The path to the output mp3 audio file.
    """
    current_task.update_state(state=states.STARTED)
    input_file_name = input_filepath.split("/")[-1].split(".")[0]
    output_file_path = f"/data/{input_file_name}.mp3"

    # Construct the FFmpeg command
    command = [
        "ffmpeg",
        "-i",
        input_filepath,
        "-vn",
        "-acodec",
        "libmp3lame",
        "-q:a",
        "4",
        "-y",
        output_file_path,
    ]

    result = subprocess.run(command, check=False, capture_output=True)
    if result.returncode != 0:
        raise Exception(f"FFmpeg command failed with error: {result.stderr.decode()}")

    print(f"Conversion completed. Output file: {output_file_path}")

    return output_file_path


@app.task(name="convert_video_to_mp3_file")
def convert_video_to_mp3(input_file):
    """
    DEPRECATED use convert_video_to_mp3 instead
    Converts a given mp4 video file to an mp3 audio file.


    Args:
        input_file (str): Base64 encoded mp4 video file.

    Returns:
        b64 (str): The base64 encoded mp3 audio file.
    """
    current_task.update_state(state=states.STARTED)
    uuidname = str(uuid.uuid4())
    with open(f"/tmp/{uuidname}.mp4", "wb") as f:
        f.write(base64.b64decode(input_file))
    input_file = f"/tmp/{uuidname}.mp4"
    output_file = f"/tmp/{uuidname}.mp3"

    # Construct the FFmpeg command
    command = [
        "ffmpeg",
        "-i",
        input_file,
        "-vn",
        "-acodec",
        "libmp3lame",
        "-q:a",
        "4",
        "-y",
        output_file,
    ]
    # Run the FFmpeg command
    subprocess.run(command, check=True)
    print(f"Conversion completed. Output file: {output_file}")

    with open(output_file, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data)
    return b64


# youtube downloader
@app.task(name="youtube_dl", bind=True)
def youtube_dl(self, url):
    """Downloads a youtube video and returns the path to the downloaded file.

    Returns:
        String: path of downloaded file
    """

    current_task.update_state(state=states.STARTED)
    uuidname = str(uuid.uuid4())
    output_file = f"/data/{uuidname}.mp4"
    downloader = YouTubeDownloader(url)
    downloader.download(output_file)
    return output_file
