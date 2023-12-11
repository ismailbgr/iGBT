from celery import Celery
import base64
import uuid
import yaml
from speech_texter import Speech2Text
import os

# Load config
config = None
with open("/app/config/config.yml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

print("config: ", config)

# Create the Celery app

app = Celery(
    "speechtexter",
    broker=config["celery"]["broker"],
    backend=config["celery"]["backend"],
)


@app.task(name="speech2text")
def speech2text(
    input_file_path,
    language_code="en-US",
    model_name=config["speechtexter"]["model_name"],
):
    output_file = input_file_path + ".txt"

    Speech2Text(
        input_file_path, output_file, language_code, model_name
    ).speech_to_text()

    with open(output_file, "r") as f:
        return f.read()


@app.task(name="speech2text_file")
def speech2text_file(
    input_file, language_code="en-US", model_name=config["speechtexter"]["model_name"]
):
    """gets the text from the audio file from the base64 encoded mp3 file

    Returns:
        str: the text from the audio file
    """

    input_file_name = str(uuid.uuid4()) + ".mp3"
    output_file = str(uuid.uuid4()) + ".txt"

    with open(input_file_name, "wb") as f:
        f.write(base64.b64decode(input_file))

    Speech2Text(
        input_file_name, output_file, language_code, model_name
    ).speech_to_text()

    with open(output_file, "r") as f:
        return f.read()
