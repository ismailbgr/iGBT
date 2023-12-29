from celery import Celery, current_task, states
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
    # TODO: speech2text should be able to detect language automatically
    # this issue requires issue #33 to be resolved
    model_name=config["speechtexter"]["model_name"],
):
    output_file = input_file_path + ".txt"

    current_task.update_state(state=states.STARTED)
    Speech2Text(
        input_file_path, output_file, language_code, model_name
    ).speech_to_text()

    with open(output_file, "r") as f:
        return f.read()
