import subprocess
from celery import Celery, current_task, states
import base64
import uuid
import yaml
from Downloader import YouTubeDownloader

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
def convert_video_to_mp3(input_file):
    """
    Converts a given mp4 video file to an mp3 audio file.

    Args:
        input_file (str): The path to the input mp4 video file.
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
@app.task(name="youtube_dl")
def youtube_dl(url):
    current_task.update_state(state=states.STARTED)
    uuidname = str(uuid.uuid4())
    downloader = YouTubeDownloader(url)
    downloader.download(f"/tmp/{uuidname}.mp4")
    with open(f"/tmp/{uuidname}.mp4", "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data)
    return b64
