from celery import Celery
import base64
import uuid
import yaml
from speech_texter import Speech2Text

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
def speech2text(input_file, language_code="en-US", model_name=config["speechtexter"]["model_name"]):
    input_file_name = str(uuid.uuid4()) + ".mp3"
    output_file = str(uuid.uuid4()) + ".txt"

    with open(input_file_name, "wb") as f:
        f.write(base64.b64decode(input_file))

    Speech2Text(
        input_file_name, output_file, language_code, model_name
    ).speech_to_text()

    with open(output_file, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")
