import subprocess
from celery import Celery, current_task, states
import base64
import uuid
import yaml

# from Downloader import YouTubeDownloader
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
    try:
        current_task.update_state(state=states.STARTED)
    except Exception as e:
        print(f" State update failed: {e}", flush=True)

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
        current_task.update_state(state=states.FAILURE)
        raise Exception(f"FFmpeg command failed with error: {result.stderr.decode()}")

    print(f"Conversion completed. Output file: {output_file_path}")

    return output_file_path


# youtube downloader
@app.task(name="youtube_dl", bind=True)
def youtube_dl(self, url):
    """Downloads a youtube video and returns the path to the downloaded file.

    Returns:
        String: path of downloaded file
    """

    import yt_dlp

    current_task.update_state(state=states.STARTED)
    uuidname = str(uuid.uuid4())
    output_file = f"/data/{uuidname}.mp3"

    def download_progress_hook(d):
        if d["status"] == "finished":
            print("Done downloading")

        if d["status"] == "downloading":
            print(f"Downloading {d['filename']}")
            print(f"ETA: {d['eta']}")
            print(f"Speed: {d['speed']}")
            print(f"Fraction downloaded: {d['_percent_str']}")

    ydl_opts = {
        "format": "bestaudio",
        "writesubtitles": True,
        "progress_hooks": [download_progress_hook],
        "outtmpl": output_file,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        # print error and retry
        print(f"Error downloading: {e}, retrying in 5 seconds.")
        current_task.retry(countdown=5, max_retries=3)

    print(f"Download completed. Output file: {output_file}")
    current_task.update_state(state=states.SUCCESS)
    return output_file
