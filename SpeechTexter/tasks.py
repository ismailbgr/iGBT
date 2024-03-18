from celery import Celery, current_task, states
import base64
import uuid
import yaml
from speech_texter import Speech2Text
import os
import webvtt
import whisper
import threading
import gc

# Load config
config = None
with open("/app/config/config.yml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

print("config: ", config)

# Load the whisper model to download the first time



def load_whisper_model():
    print("Loading whisper model", flush=True)
    import torch
    temp_model = whisper.load_model("base")
    print("Whisper model loaded", flush=True)
    del temp_model
    print("Whisper model deleted", flush=True)
    gc.collect()
    print("Garbage collected", flush=True)
    torch.cuda.empty_cache()
    print("Cuda cache emptied", flush=True)



# Load the whisper model to download the first time
threading.Thread(target=load_whisper_model).start()


# Create the Celery app

app = Celery(
    "speechtexter",
    broker=config["celery"]["broker"],
    backend=config["celery"]["backend"],
)


@app.task(name="speech2text")
def speech2text(
    input_file_path,
    language_code=None,
    model_name=config["speechtexter"]["model_name"],
    model_size=config["speechtexter"]["model_size"],
):
    output_file = input_file_path + ".txt"

    # check if there is any subtitle downloaded
    if os.path.exists(input_file_path[:-4] + ".en.vtt"):
        print("Subtitle already exists, skipping speech to text", flush=True)
        # convert vtt to txt
        vtt = webvtt.read(input_file_path[:-4] + ".en.vtt")
        with open(output_file, "w") as f:
            for line in vtt:
                f.write(line.text + "\n")
        with open(output_file, "r") as f:
            return f.read()

    try:
        current_task.update_state(state=states.STARTED)
    except Exception as e:
        print(f" State update failed: {e}", flush=True)
    Speech2Text(
        input_file_path, output_file, language_code, model_name, model_size=model_size
    ).speech_to_text()

    with open(output_file, "r") as f:
        return f.read()
