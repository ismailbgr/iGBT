from celery import Celery
import uuid
import yaml
from tts_lib import iGBTTS

# Load config
config = None
with open("/app/config/config.yml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

print("config: ", config)

# Create the Celery app

app = Celery(
    "tts",
    broker=config["celery"]["broker"],
    backend=config["celery"]["backend"],
)


@app.task(name="tts")
def tts(model,text,lang="en",output_filename=None):
    tts_obj = iGBTTS(model)
    if output_filename is not None:
        output_filename= f"/data/{output_filename}.wav"
    else:
        output_filename = f"/data/{uuid.uuid4()}.wav"
    tts_obj.tts(text=text,lang=lang,output_filename=output_filename)

    return output_filename